# argo-workflows-ci-example

## Steps to Run

- Install

```shell
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.24.3+k3s1 sh -s - --advertise-address 159.138.150.166 --node-external-ip 159.138.150.166
cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
kubectl config set-cluster default --server=https://159.138.150.166:6443
kubectl apply -k bootstrap/argocd
kubectl -n argocd rollout status statefulset/argocd-application-controller
kubectl -n argocd rollout status deployment/argocd-repo-server
kubectl -n argocd apply -f default.yml
sleep 30
kubectl -n nfs-server-provisioner rollout status statefulset/nfs-server-provisioner
kubectl -n argo rollout status deployment/workflow-controller
kubectl -n argo rollout status deployment/argo-server
kubectl create -f docker-config.yaml
kubectl apply -f bootstrap/cert-manager/manifest.yaml
kubectl -n cert-manager rollout status deployment/cert-manager-webhook
kubectl apply -f bootstrap/cert-manager/ClusterIssuer.yaml
kubectl -n argo create -f workflow.yml
kubectl -n argocd delete application final-application
```

- Get Argo CD Password

```shell
PASSWORD=`kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d`
echo "Complete. You should be able to navigate to https://argocd.abu.pub admin ${PASSWORD}"
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
