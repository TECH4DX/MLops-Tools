# Machine Learning Operations

## Env

- *.abu.pub is your managed domain

- IP

```shell
IP=`ifconfig eth0 | grep "inet " | awk '{print $2}'`
```

## Deploy Docker

```shell
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

## Deploy Kubernetes

```shell
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.24.3+k3s1 sh -s - --advertise-address ${IP} --node-external-ip ${IP}
mkdir /root/.kube/
ln -sf /etc/rancher/k3s/k3s.yaml /root/.kube/config
kubectl config set-cluster default --server=https://${IP}:6443
apt update
apt install nfs-common -y
```

## Deploy cert-manager

```shell
kubectl create -f cert-manager/namespace.yaml
kubectl create -f cert-manager/manifest.yaml
kubectl -n cert-manager rollout status deployment/cert-manager-webhook
```

- Add DNS record Use Cloudflare

```text
Type: A
Name: *
IPv4 address: ${IP}
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

```shell
kubectl apply -k argocd/
kubectl -n argocd rollout status statefulset/argocd-application-controller
kubectl -n argocd rollout status deployment/argocd-repo-server
```

- Get Argo CD Password

```shell
PASSWORD=`kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d`
echo "Complete. You should be able to navigate to https://argocd.abu.pub admin ${PASSWORD}"
```

## Deploy Workflow

- Deploy

```shell
kubectl create namespace argo
kubectl apply -k argo-workflows/
kubectl -n argo rollout status deployment/workflow-controller
kubectl -n argo rollout status deployment/argo-server
echo "https://argo.abu.pub"
```

## Deploy NFS Server Provisioner

```shell
kubectl delete sc local-path
kubectl create -f applications/nfs-server-provisioner.yml
kubectl -n nfs-server-provisioner rollout status statefulset/nfs-server-provisioner
```

## Deploy Postgres

```shell
kubectl create -f applications/postgresql.yml
kubectl -n postgresql rollout status statefulset/postgresql-postgresql
export POSTGRES_PASSWORD=$(kubectl get secret --namespace postgresql postgresql -o jsonpath="{.data.postgresql-password}" | base64 --decode)
kubectl run postgresql-client --rm --tty -i --restart='Never' --namespace postgresql --image docker.io/bitnami/postgresql:11.14.0-debian-10-r28 --env="PGPASSWORD=$POSTGRES_PASSWORD" --command -- psql --host postgresql -U postgres -d postgres -p 5432
create database registry;
create database notary_signer;
create database notary_server;
\l
\q
kubectl -n postgresql delete pods postgresql-client
echo ${POSTGRES_PASSWORD}
```

## Deploy Harbor

> Modify Domain & PG Password in harbor/values.yaml & harbor/templates/Certificate.yaml

```shell
kubectl create -f applications/harbor.yml
kubectl -n harbor rollout status deployment harbor-core
echo "https://harbor.abu.pub admin OpenSource@2022"
```

## Deploy Argo Events

```shell
kubectl create namespace argo-events
kubectl create -f argo-events/install.yaml
kubectl create -n argo-events -f argo-events/eventbus-native.yaml
kubectl create -n argo-events -f argo-events/sensor-rbac.yaml
kubectl create -n argo-events -f argo-events/workflow-rbac.yaml
kubectl create -f argo-events/role_sensor.yaml
kubectl create -f argo-events/rolebinding_sensor.yaml
kubectl create -f argo-events/SA.yaml
kubectl create -n argo-events -f argo-events/webhook.yaml
kubectl -n argo-events port-forward $(kubectl -n argo-events get pod -l eventsource-name=webhook -o name) 12000:12000 &
curl -d '{"message":"this is my first webhook"}' -H "Content-Type: application/json" -X POST http://localhost:12000/example
kubectl -n argo-events get workflows
```

## Deploy MLOps WorkflowTemplate

- Deploy

```shell
kubectl create -f mlops/Secret.yaml
kubectl create -f mlops/EventSource.yaml
kubectl create -f mlops/Ingress.yaml
kubectl -n argo create secret docker-registry docek-harbor --docker-server=https://harbor.test.abu.pub --docker-username=admin --docker-password=OpenSource@2022 --docker-email=abuxliu@gmail.com
kubectl -n argo create -f mlops/WorkflowTemplate.yaml
```

## Deploy mnist Basic

- Deploy

```shell
kubectl create -f mnist-basic/ns.yaml
kubectl -n mnist-demo create -f mnist-basic/secret.yaml
kubectl -n mnist-demo create -f mnist-basic/create-serviceaccounts.yaml
kubectl -n mnist-demo create -f mnist-basic/Ingress.yaml
```

## Deploy MLOps

- Deploy

```shell
# Manual
kubectl -n argo create -f mlops/Workflow.yaml
# or Auto
# kubectl create -f mlops/Sensor.yaml
```

## Reference

- [Deploy Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script)

- [Machine Learning Operations](https://ml-ops.org/)

- [Cloudflare - cert-manager Documentation](https://cert-manager.io/docs/configuration/acme/dns01/cloudflare/)

- [Argo Events Quick Start](https://argoproj.github.io/argo-events/quick_start/)

- [Get GitHub Token](https://argoproj.github.io/argo-events/eventsources/setup/github/)
