/*
Copyright 2022.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package controllers

import (
	"context"
	"fmt"
	"time"

	"gopkg.in/yaml.v3"
	appsv1 "k8s.io/api/apps/v1"
	v1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
	"sigs.k8s.io/controller-runtime/pkg/event"
	"sigs.k8s.io/controller-runtime/pkg/log"
	"sigs.k8s.io/controller-runtime/pkg/predicate"

	lazykoalav1alpha1 "github.com/MrSupiri/LazyKoala/api/v1alpha1"
)

// InspectorReconciler reconciles a Inspector object
type InspectorReconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

type ScrapePoint struct {
	Name        string  `yaml:"name"`
	ServiceName string  `yaml:"serviceName"`
	Namespace   string  `yaml:"namespace"`
	Node        *string `yaml:"node"`
	IsService   bool    `yaml:"isService"`
}

//+kubebuilder:rbac:groups=lazykoala.isala.me,resources=inspectors,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=lazykoala.isala.me,resources=inspectors/status,verbs=get;update;patch
//+kubebuilder:rbac:groups=lazykoala.isala.me,resources=inspectors/finalizers,verbs=update
//+kubebuilder:rbac:groups="",resources=pods;services;namespaces,verbs=get;watch;list
//+kubebuilder:rbac:groups="apps",resources=deployments,verbs=get;watch;list
//+kubebuilder:rbac:groups="",resources=configmaps,verbs=get;watch;list;update;patch
//+kubebuilder:rbac:groups="",resources=events,verbs=create;patch

// Reconcile is part of the main kubernetes reconciliation loop which aims to
// move the current state of the cluster closer to the desired state.
// TODO(user): Modify the Reconcile function to compare the state specified by
// the Inspector object against the actual cluster state, and then
// perform operations to make the cluster state reflect the state specified by
// the user.
//
// For more details, check Reconcile and its Result here:
// - https://pkg.go.dev/sigs.k8s.io/controller-runtime@v0.11.0/pkg/reconcile
func (r *InspectorReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	logger := log.FromContext(ctx)

	logger.Info("Reconciling")

	var inspector lazykoalav1alpha1.Inspector
	if err := r.Get(ctx, req.NamespacedName, &inspector); err != nil {
		return ctrl.Result{Requeue: false}, client.IgnoreNotFound(err)
	}

	// name of our custom finalizer
	finalizerName := "inspector.lazykoala.isala.me/finalizer"
	// examine DeletionTimestamp to determine if object is under deletion
	if inspector.ObjectMeta.DeletionTimestamp.IsZero() {
		// The object is not being deleted, so if it does not have our finalizer,
		// then lets add the finalizer and update the object. This is equivalent
		// registering our finalizer.
		if !controllerutil.ContainsFinalizer(&inspector, finalizerName) {
			controllerutil.AddFinalizer(&inspector, finalizerName)
			if err := r.Update(ctx, &inspector); err != nil {
				return ctrl.Result{}, err
			}
		}
	} else {
		// The object is being deleted
		if controllerutil.ContainsFinalizer(&inspector, finalizerName) {
			// our finalizer is present, so lets handle any external dependency
			if err := r.removeMonitoredIPs(&inspector); err != nil {
				// if fail to delete the external dependency here, return with error
				// so that it can be retried
				return ctrl.Result{}, err
			}

			// remove our finalizer from the list and update it.
			controllerutil.RemoveFinalizer(&inspector, finalizerName)
			if err := r.Update(ctx, &inspector); err != nil {
				return ctrl.Result{}, err
			}
		}

		// Stop reconciliation as the item is being deleted
		return ctrl.Result{}, nil
	}
	// Get the intended deployment
	var deploymentRef appsv1.Deployment
	if err := r.Get(ctx, types.NamespacedName{
		Namespace: inspector.Spec.Namespace,
		Name:      inspector.Spec.DeploymentRef,
	}, &deploymentRef); err != nil {
		return ctrl.Result{}, err
	}

	scrapePoints := make(map[string]ScrapePoint)

	// Get Pods for that deployment
	selector := client.MatchingLabels(deploymentRef.Spec.Selector.MatchLabels)
	inspector.Status.PodsSelector = selector
	var podList v1.PodList
	if err := r.List(ctx, &podList, &selector); client.IgnoreNotFound(err) != nil {
		logger.Error(err, fmt.Sprintf("failed to pods for deployment %s", deploymentRef.ObjectMeta.Name))
		return ctrl.Result{}, err
	}

	// Create Scrape point for each pod
	for _, pod := range podList.Items {
		scrapePoints[pod.Status.PodIP] = ScrapePoint{
			Name:        pod.ObjectMeta.Name,
			ServiceName: inspector.Spec.DeploymentRef,
			Namespace:   inspector.Spec.Namespace,
			Node:        &pod.Spec.NodeName,
			IsService:   false,
		}
	}

	// Create Scrape point for Cluster DNS for the deployment
	var serviceRef v1.Service
	if err := r.Get(ctx, types.NamespacedName{
		Namespace: inspector.Spec.Namespace,
		Name:      inspector.Spec.ServiceRef,
	}, &serviceRef); err != nil {
		return ctrl.Result{}, err
	}

	scrapePoints[serviceRef.Spec.ClusterIP] = ScrapePoint{
		Name:        serviceRef.ObjectMeta.Name,
		ServiceName: inspector.Spec.DeploymentRef,
		Namespace:   inspector.Spec.Namespace,
		Node:        nil,
		IsService:   true,
	}

	// Get the Gazer config file
	var configMap v1.ConfigMap
	if err := r.Get(ctx, types.NamespacedName{
		Namespace: "lazy-koala",
		Name:      "gazer-config",
	}, &configMap); err != nil {
		return ctrl.Result{}, err
	}

	// Phase the config.yaml
	configData := make(map[string]ScrapePoint)
	if err := yaml.Unmarshal([]byte(configMap.Data["config.yaml"]), &configData); err != nil {
		return ctrl.Result{}, err
	}

	// Remove all the existing scrape points created from this Inspector
	for _, ip := range inspector.Status.MonitoredIPs {
		if _, ok := configData[ip]; ok {
			delete(configData, ip)
		}
	}

	// Add the new scrape points
	for k, v := range scrapePoints {
		configData[k] = v
	}

	// Encode the config.yaml
	encodedConfig, err := yaml.Marshal(&configData)
	if err != nil {
		return ctrl.Result{}, err
	}

	// Patch the config file
	configMap.Data["config.yaml"] = string(encodedConfig)
	if err := r.Update(ctx, &configMap); err != nil {
		return ctrl.Result{}, err
	}

	// Update local status
	var MonitoredIPs []string
	for k := range scrapePoints {
		MonitoredIPs = append(MonitoredIPs, k)
	}
	inspector.Status.MonitoredIPs = MonitoredIPs
	inspector.Status.Status = lazykoalav1alpha1.Running

	if err := r.Status().Update(ctx, &inspector); err != nil {
		return ctrl.Result{}, err
	}

	return ctrl.Result{RequeueAfter: time.Minute}, nil
}

func (r *InspectorReconciler) removeMonitoredIPs(inspector *lazykoalav1alpha1.Inspector) error {
	// Get the Gazer config file
	var configMap v1.ConfigMap
	if err := r.Get(context.Background(), types.NamespacedName{
		Namespace: "lazy-koala",
		Name:      "gazer-config",
	}, &configMap); err != nil {
		return err
	}

	// Phase the config.yaml
	configData := make(map[string]ScrapePoint)
	if err := yaml.Unmarshal([]byte(configMap.Data["config.yaml"]), &configData); err != nil {
		return err
	}

	// Remove all the existing scrape points created from this Inspector
	for _, ip := range inspector.Status.MonitoredIPs {
		if _, ok := configData[ip]; ok {
			delete(configData, ip)
		}
	}

	// Encode the config.yaml
	encodedConfig, err := yaml.Marshal(&configData)
	if err != nil {
		return err
	}

	// Patch the config file
	configMap.Data["config.yaml"] = string(encodedConfig)
	if err := r.Update(context.Background(), &configMap); err != nil {
		return err
	}
	return nil
}

// SetupWithManager sets up the controller with the Manager.
func (r *InspectorReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&lazykoalav1alpha1.Inspector{}).
		WithEventFilter(eventFilter()).
		Complete(r)
}

func eventFilter() predicate.Predicate {
	return predicate.Funcs{
		UpdateFunc: func(e event.UpdateEvent) bool {
			// Ignore updates to CDR status in which case metadata.Generation does not change
			return e.ObjectOld.GetGeneration() != e.ObjectNew.GetGeneration()
		},
	}
}
