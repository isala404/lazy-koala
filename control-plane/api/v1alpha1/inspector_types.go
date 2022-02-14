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

package v1alpha1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"sigs.k8s.io/controller-runtime/pkg/client"
)

// EDIT THIS FILE!  THIS IS SCAFFOLDING FOR YOU TO OWN!
// NOTE: json tags are required.  Any new fields you add must have json tags for the fields to be serialized.

// +kubebuilder:validation:Required
type DeploymentReference struct {
	Name      string `json:"name"`
	Namespace string `json:"namespace"`
}

// InspectorSpec defines the desired state of Inspector
type InspectorSpec struct {
	// INSERT ADDITIONAL SPEC FIELDS - desired state of cluster
	// Important: Run "make" to regenerate code after modifying this file

	// Foo is an example field of Inspector. Edit inspector_types.go to remove/update
	DeploymentRef string `json:"deploymentRef"`
	ServiceRef    string `json:"serviceRef"`
	Namespace     string `json:"namespace"`
	ModelURI      string `json:"modelURI"`
}

type Status string

const (
	Creating Status = "Creating"
	Running  Status = "Running"
	Error    Status = "Error"
)

// InspectorStatus defines the observed state of Inspector
type InspectorStatus struct {
	// INSERT ADDITIONAL STATUS FIELD - define observed state of cluster
	// Important: Run "make" to regenerate code after modifying this file
	MonitoredIPs []string              `json:"monitoredIPs"`
	PodsSelector client.MatchingLabels `json:"podsSelector"`
	// +kubebuilder:validation:Enum=Creating;Running;Error
	Status Status `json:"status"`
}

//+kubebuilder:object:root=true
//+kubebuilder:subresource:status
//+kubebuilder:printcolumn:JSONPath=".spec.namespace",name="Namespace",type="string"
//+kubebuilder:printcolumn:JSONPath=".spec.deploymentRef",name="Target Deployment",type="string"
//+kubebuilder:printcolumn:JSONPath=".spec.serviceRef",name="Target ClusterIP",type="string"
//+kubebuilder:printcolumn:JSONPath=".spec.modelURI",name="Model URI",type="string"
//+kubebuilder:printcolumn:JSONPath=".status.status",name="Status",type="string"

// Inspector is the Schema for the inspectors API
type Inspector struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   InspectorSpec   `json:"spec,omitempty"`
	Status InspectorStatus `json:"status,omitempty"`
}

//+kubebuilder:object:root=true

// InspectorList contains a list of Inspector
type InspectorList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []Inspector `json:"items"`
}

func init() {
	SchemeBuilder.Register(&Inspector{}, &InspectorList{})
}
