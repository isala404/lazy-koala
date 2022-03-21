package main

import (
	"embed"
	"io/fs"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"path"
	"strings"

	"github.com/gorilla/mux"
	"github.com/rs/cors"
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
	u, _ := url.Parse("http://127.0.0.1:8001/")
	r := mux.NewRouter()

	r.PathPrefix("/k8s").HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		proxy := httputil.NewSingleHostReverseProxy(u)

		r.URL.Path = "/" + strings.Join(strings.Split(r.URL.Path, "/")[2:], "/")

		log.Printf("Proxying Request from %s to KubeAPI on %s\n", r.RemoteAddr, r.URL.Path)

		proxy.ServeHTTP(w, r)
	})

	r.PathPrefix("/").Handler(clientHandler())

	corsOpts := cors.New(cors.Options{
		AllowedOrigins: []string{"*"},
		AllowedMethods: []string{
			http.MethodGet,
			http.MethodDelete,
			http.MethodPost,
		},
	})

	log.Println("Client app started on port :8090")

	if err := http.ListenAndServe(":8090", corsOpts.Handler(r)); err != http.ErrServerClosed {
		log.Fatal("Receiver webserver crashed: %s", err)
		os.Exit(1)
	}
}
