package main

import (
	"fmt"
	"net/http"
  "time"
)

func getIPAddress(r *http.Request) string {

  ipAddress := r.RemoteAddr
	fwdAddress := r.Header.Get("X-Forwarded-For")
	if fwdAddress != "" {
		ipAddress = fwdAddress
	}
  return ipAddress
}

func handlerPing(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("pong"))
	fmt.Println(time.Now(), getIPAddress(r), r.Method, r.RequestURI, r.UserAgent())
}

func main() {
	http.HandleFunc("/ping", handlerPing)

	fmt.Println("ping listening on 0.0.0.0, port 80")
	err := http.ListenAndServe(":8081", nil)

	if err != nil {
		fmt.Println("Error starting ping server: ", err)
	}
}
