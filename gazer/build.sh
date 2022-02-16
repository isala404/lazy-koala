TAG=$(date +%s)

docker build . -t ghcr.io/mrsupiri/lazy-koala/gazer:$TAG
minikube image load ghcr.io/mrsupiri/lazy-koala/gazer:$TAG
kubectl set image daemonsets.apps gazer gazer=ghcr.io/mrsupiri/lazy-koala/gazer:$TAG -n lazy-koala
kubectl scale --replicas 0 deployment prometheus -n lazy-koala
sleep 1
kubectl scale --replicas 1 deployment prometheus -n lazy-koala