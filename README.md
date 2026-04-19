# kubernetes-application-code

Two FastAPI microservices with structured JSON logging, visualised in **Grafana** via the **Loki + Promtail** stack — all running on Kubernetes.

```
app-service    →  GET /products, GET /products/{id}, GET /simulate-error
worker-service →  POST /tasks,   GET /tasks/{id},    GET /simulate-error
```

---

## Project structure

```
├── app-service/          FastAPI service 1 (products)
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── worker-service/       FastAPI service 2 (task processor)
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
└── k8s/
    ├── namespace.yaml
    ├── app-service/      Deployment + Service
    ├── worker-service/   Deployment + Service
    ├── loki/             Log store (ConfigMap + Deployment + Service)
    ├── promtail/         Log shipper DaemonSet (RBAC + ConfigMap + DaemonSet)
    └── grafana/          Visualisation (ConfigMap + Deployment + NodePort Service)
```

---

## Quick start (minikube)

### 1. Build images inside minikube's Docker daemon

```bash
eval $(minikube docker-env)

docker build -t app-service:latest    ./app-service
docker build -t worker-service:latest ./worker-service
```

### 2. Apply all manifests

```bash
kubectl apply -f k8s/namespace.yaml

kubectl apply -f k8s/loki/
kubectl apply -f k8s/promtail/
kubectl apply -f k8s/grafana/

kubectl apply -f k8s/app-service/
kubectl apply -f k8s/worker-service/
```

### 3. Wait for everything to be ready

```bash
kubectl get pods -n logging-demo -w
```

### 4. Open Grafana

```bash
minikube service grafana -n logging-demo
```

Login: **admin / admin**

Go to **Explore → Loki** and run a query like:

```logql
{app="app-service"}
{app="worker-service"}
{level="ERROR"}
```

---

## Generate some logs

Port-forward each service:

```bash
kubectl port-forward svc/app-service    -n logging-demo 8001:80
kubectl port-forward svc/worker-service -n logging-demo 8002:80
```

Hit a few endpoints:

```bash
# app-service
curl http://localhost:8001/
curl http://localhost:8001/products
curl http://localhost:8001/products/1
curl http://localhost:8001/products/99   # → 404 warning log
curl http://localhost:8001/simulate-error # → 500 error log

# worker-service
curl http://localhost:8002/
curl -X POST http://localhost:8002/tasks -H "Content-Type: application/json" -d '{"name":"job1"}'
curl http://localhost:8002/simulate-error # → 500 error log
```

---

## How it works

```
FastAPI pod (stdout JSON logs)
        │
  /var/log/pods/  (host)
        │
    Promtail (DaemonSet)
        │  relabels: app, namespace, pod, level
        ▼
      Loki  (log store)
        │
     Grafana (query & visualise)
```

Each log line is emitted as JSON:

```json
{
  "timestamp": "2026-04-19T10:00:00+00:00",
  "level": "INFO",
  "service": "app-service",
  "logger": "app-service",
  "message": "Listing all products"
}
```

Promtail parses `level` and `service` fields and promotes them to Loki labels, so you can filter by either service independently in Grafana.
