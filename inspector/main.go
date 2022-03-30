package main

import (
	"crypto/tls"
	"crypto/x509"
	"embed"
	"fmt"
	"io/fs"
	"io/ioutil"
	"log"
	"net"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"path"
	"strings"

	"github.com/gorilla/mux"
)

const (
	tokenFile  = "/var/run/secrets/kubernetes.io/serviceaccount/token"
	rootCAFile = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
)

//go:embed ui/*
var content embed.FS

type fsFunc func(name string) (fs.File, error)

func (f fsFunc) Open(name string) (fs.File, error) {
	return f(name)
}

func clientHandler() http.Handler {
	handler := fsFunc(func(name string) (fs.File, error) {
		assetPath := path.Join("ui", name)

		// If we can't find the asset, return the default index.html
		// content
		f, err := content.Open(assetPath)
		if os.IsNotExist(err) {
			return content.Open("ui/index.html")
		}

		// Otherwise assume this is a legitimate request routed
		// correctly
		return f, err
	})

	return http.FileServer(http.FS(handler))
}

func main() {

	// Setup proxy data
	token, err := ioutil.ReadFile(tokenFile)
	if err != nil {
		log.Println("failed to read the token from kubernetes secrets")
	}
	CAData, err := ioutil.ReadFile(rootCAFile)
	if err != nil {
		log.Println("failed to read the CA Data from kubernetes secrets")
	}

	// Get the SystemCertPool, continue with an empty pool on error
	rootCAs, _ := x509.SystemCertPool()
	if rootCAs == nil {
		rootCAs = x509.NewCertPool()
	}

	// Append our cert to the system pool
	if ok := rootCAs.AppendCertsFromPEM(CAData); !ok {
		log.Println("failed to append k8s custom CA, using system certs only")
	}

	if err != nil {
		log.Println("it seems like operator is not running in side cluster, kube-api proxy will not operate as intended")
	}

	proxyTransport := &http.Transport{TLSClientConfig: &tls.Config{
		RootCAs: rootCAs,
	}}

	kube_endpoint, _ := url.Parse("https://" + net.JoinHostPort(os.Getenv("KUBERNETES_SERVICE_HOST"), os.Getenv("KUBERNETES_SERVICE_PORT")))

	prom_endpoint, _ := url.Parse(os.Getenv("PROMETHEUS_END_POINT"))
	r := mux.NewRouter()

	r.PathPrefix("/k8s").HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		log.Printf("Proxying %s Request from %s to KubeAPI on %s\n", r.Method, r.RemoteAddr, r.URL.Path)

		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Private-Network", "true")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		w.Header().Set("Access-Control-Allow-Methods", "OPTIONS, GET, POST, DELETE")
		if r.Method == http.MethodOptions {
			w.WriteHeader(204)
			return
		}
		proxy := httputil.NewSingleHostReverseProxy(kube_endpoint)
		proxy.Transport = proxyTransport
		r.Header.Add("Authorization", fmt.Sprintf("Bearer %s", string(token)))

		r.URL.Path = "/" + strings.Join(strings.Split(r.URL.Path, "/")[2:], "/")

		proxy.ServeHTTP(w, r)
	}).Methods(http.MethodGet, http.MethodPost, http.MethodDelete, http.MethodOptions)

	r.PathPrefix("/prom").HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		proxy := httputil.NewSingleHostReverseProxy(prom_endpoint)

		r.URL.Path = "/" + strings.Join(strings.Split(r.URL.Path, "/")[2:], "/")

		log.Printf("Proxying Request from %s to prometheus on %s\n", r.RemoteAddr, r.URL.Path)

		proxy.ServeHTTP(w, r)
		// fmt.Printf("proxy.ModifyResponse: %v\n", proxy.ModifyResponse)
	}).Methods(http.MethodGet, http.MethodOptions)

	r.PathPrefix("/").Handler(clientHandler())

	r.Use(mux.CORSMethodMiddleware(r))

	log.Println("Client app started on port :8090")

	if err := http.ListenAndServe(":8090", r); err != http.ErrServerClosed {
		log.Fatal("Receiver webserver crashed: %s", err)
		os.Exit(1)
	}
}
