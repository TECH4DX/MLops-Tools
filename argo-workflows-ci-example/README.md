# Machine Learning Operations

## Env

- 10.95.160.8 is your server's ip

- *.test.abu.pub is your managed domain

## Deploy Kubernetes

```shell
# 
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.24.3+k3s1 sh -s - --advertise-address 10.95.160.8 --node-external-ip 10.95.160.8
mkdir /root/.kube/
ln -sf /etc/rancher/k3s/k3s.yaml /root/.kube/config
kubectl config set-cluster default --server=https://10.95.160.8:6443
```

## Deploy cert-manager

- Create namespace

```shell
kubectl create -f cert-manager/namespace.yaml
```

- Deploy

```shell
kubectl create -f cert-manager/manifest.yaml
```

- Check

```shell
kubectl -n cert-manager rollout status deployment/cert-manager-webhook
```

- Add DNS record Use Cloudflare

```text
Type: A
Name: *.test
IPv4 address: 10.95.160.8
Proxy status: DNS only
TTL: Auto
```

- Create Cloudflare Custom Token Use Cloudflare, and Modify cert-manager/ClusterIssuer.yaml, see Reference 2

```text
api-token: sZtljE0iuaNy1pb1veCv3jln_B85cRkZ8SPOROe_
```

- Create Secret & ClusterIssuer

```shell
kubectl create -f cert-manager/ClusterIssuer.yaml
```

## Deploy Argo CD

- Deploy

```shell
kubectl apply -k argocd/
```

- Check

```shell
kubectl -n argocd rollout status statefulset/argocd-application-controller
kubectl -n argocd rollout status deployment/argocd-repo-server
```

- Get Argo CD Password

```shell
PASSWORD=`kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d`
echo "Complete. You should be able to navigate to https://argocd.test.abu.pub admin ${PASSWORD}"
```

## Deploy Workflow

- Deploy

```shell
kubectl create namespace argo
kubectl apply -k argo-workflows/
```

- Check

```shell
kubectl -n argo rollout status deployment/workflow-controller
kubectl -n argo rollout status deployment/argo-server
```

## Deploy NFS Server Provisioner

- Deploy

```shell
kubectl create -f applications/nfs-server-provisioner.yml
```

- Check

```shell
kubectl -n nfs-server-provisioner rollout status statefulset/nfs-server-provisioner
```

## Deploy Postgres

- Deploy

```shell
kubectl create -f applications/postgresql.yml
```

- Check

```shell
kubectl -n postgresql rollout status statefulset/postgresql-postgresql
```

## Deploy Harbor

- Deploy

```shell

```

- Check

```shell

```

## Other

```shell
kubectl create -f docker-config.yaml
kubectl -n argo create -f workflow.yml
kubectl -n argocd delete application final-application
```

- Install Argo Events

```shell
kubectl create namespace argo-events
kubectl create -f bootstrap/argo-events/install.yaml
kubectl apply -n argo-events -f bootstrap/argo-events/eventbus-native.yaml
# kubectl apply -n argo -f https://raw.githubusercontent.com/argoproj/argo-workflows/stable/manifests/install.yaml
kubectl apply -n argo-events -f https://raw.githubusercontent.com/argoproj/argo-events/stable/examples/event-sources/webhook.yaml
# sensor rbac
kubectl apply -n argo-events -f https://raw.githubusercontent.com/argoproj/argo-events/master/examples/rbac/sensor-rbac.yaml
 # workflow rbac
kubectl apply -n argo-events -f https://raw.githubusercontent.com/argoproj/argo-events/master/examples/rbac/workflow-rbac.yaml
kubectl apply -n argo-events -f https://raw.githubusercontent.com/argoproj/argo-events/stable/examples/sensors/webhook.yaml
kubectl -n argo-events port-forward $(kubectl -n argo-events get pod -l eventsource-name=webhook -o name) 12000:12000 &
curl -d '{"message":"this is my first webhook"}' -H "Content-Type: application/json" -X POST http://localhost:12000/example
kubectl -n argo-events get workflows | grep "webhook"

# [Quick Start](https://argoproj.github.io/argo-events/quick_start/)
# [Get GitHub Token](https://argoproj.github.io/argo-events/eventsources/setup/github/)
# .data.token

kubectl create -f bootstrap/argo-events/Secret.yaml
kubectl create -f bootstrap/argo-events/EventSource.yaml
kubectl create -f bootstrap/argo-events/Ingress.yaml
kubectl create -f bootstrap/argo-events/Sensor.yaml
kubectl create -f role_sensor.yaml
kubectl create -f rolebinding_sensor.yaml
```

## Reference

1. [Machine Learning Operations](https://ml-ops.org/)

2. [Cloudflare - cert-manager Documentation](https://cert-manager.io/docs/configuration/acme/dns01/cloudflare/)
