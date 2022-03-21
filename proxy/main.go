package main

import (
	"fmt"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"strings"

	"github.com/gorilla/mux"
	"github.com/rs/cors"
)

func main() {
	u, _ := url.Parse("http://127.0.0.1:8001/")
	r := mux.NewRouter()

	r.PathPrefix("/k8s").HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		proxy := httputil.NewSingleHostReverseProxy(u)

		r.URL.Path = "/" + strings.Join(strings.Split(r.URL.Path, "/")[2:], "/")

		fmt.Println(r.URL.Path)

		proxy.ServeHTTP(w, r)
	})

	corsOpts := cors.New(cors.Options{
		AllowedOrigins: []string{"*"},
		AllowedMethods: []string{
			http.MethodGet,
			http.MethodDelete,
			http.MethodPost,
		},
	})

	if err := http.ListenAndServe(":8090", corsOpts.Handler(r)); err != http.ErrServerClosed {
		log.Fatal("Receiver webserver crashed: %s", err)
		os.Exit(1)
	}
}
