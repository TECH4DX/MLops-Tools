# Machine Learning Operations

## Env

- *.mlops.pub is your managed domain

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
You need to configure the Kubenetes environment before deploy your own workflows. Fortunately, it is extremely convenient to install, see [k8s-installation.md](../k8s-installation.md). Make sure you have `kubectl` configured correctly on your machine, use `kubectl apply` command with installation yaml file in related folder to install components needed:

## Deploy cert-manager

```shell
kubectl create -f cert-manager/namespace.yaml
kubectl create -f cert-manager/manifest.yaml
kubectl rollout status deployment/cert-manager-webhook -n cert-manager
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
kubectl rollout status statefulset/argocd-application-controller -n argocd
kubectl rollout status deployment/argocd-repo-server -n argocd
```

- Get Argo CD Password

```shell
PASSWORD=`kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d`
echo "Complete. You should be able to navigate to https://cd.mlops.pub admin ${PASSWORD}"
```

## Deploy Workflow

- Deploy

```shell
kubectl apply -k argo-workflows/
kubectl rollout status deployment/workflow-controller -n argo 
kubectl rollout status deployment/argo-server -n argo
```

- Get Argo Workflow Password

```shell
SECRET=$(kubectl get sa argo-server -n argo -o=jsonpath='{.secrets[0].name}')
ARGO_TOKEN="Bearer $(kubectl get secret $SECRET -n argo -o=jsonpath='{.data.token}' | base64 --decode)"
echo "https://workflows.mlops.pub"
echo "${ARGO_TOKEN}"
#output: Bearer ZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNkltS...
```

## Deploy NFS Server Provisioner

```shell
kubectl delete sc local-path
kubectl create -f applications/nfs-server-provisioner.yml
kubectl rollout status statefulset/nfs-server-provisioner -n nfs-server-provisioner
```

## Deploy Postgres

```shell
kubectl create -f applications/postgresql.yml
kubectl rollout status statefulset/postgresql-postgresql -n postgresql
export POSTGRES_PASSWORD=$(kubectl get secret --namespace postgresql postgresql -o jsonpath="{.data.postgresql-password}" | base64 --decode)
kubectl run postgresql-client --rm --tty -i --restart='Never' --namespace postgresql --image docker.io/bitnami/postgresql:11.14.0-debian-10-r28 --env="PGPASSWORD=$POSTGRES_PASSWORD" --command -- psql --host postgresql -U postgres -d postgres -p 5432
create database registry;
create database notary_signer;
create database notary_server;
\l
\q
kubectl delete pods postgresql-client -n postgresql
echo ${POSTGRES_PASSWORD}
```

## Deploy Harbor

> Modify Domain & PG Password in harbor/values.yaml & harbor/templates/Certificate.yaml

```shell
kubectl create -f applications/harbor.yml
kubectl rollout status deployment harbor-core -n harbor
echo "https://harbor.mlops.pub admin OpenSource@2022"
```

## Deploy Argo Events

```shell
kubectl apply -k argo-events/

curl -d '{"message":"this is my first webhook"}' -H "Content-Type: application/json" -X POST http://argoevents-webhook-demo.mlops.pub/example
kubectl get workflows -n argo-events
```

## Deploy MLOps WorkflowTemplate

> Modify Domain in EventSource.yaml & Ingress.yaml

```shell
kubectl create -f xops/github/namespace.yaml
kubectl create -f xops/github/Secret.yaml
kubectl create -f xops/github/EventBus.yaml
kubectl create -f xops/github/EventSource.yaml
kubectl create -f xops/github/Ingress.yaml
# create secret for harbor
kubectl create secret docker-registry docek-harbor \
--docker-server=https://harbor.mlops.pub \
--docker-username=admin \
--docker-password=OpenSource@2022 \
--docker-email=guoqiang.qi1@gmail.com \
-n github-mnist
# Deploy WorkflowTemplate
kubectl create -f xops/github/WorkflowTemplate.yaml
```

## Deploy mnist example

```shell
kubectl create -f xops/github/create-serviceaccounts.yaml
# Trigger workflows with github push events
kubectl create -f xops/github/Sensor.yaml
# Trigger workflows immediately
kubectl create -f xops/github/Workflow.yaml
```

## Reference

- [Deploy Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script)

- [Machine Learning Operations](https://ml-ops.org/)

- [Cloudflare - cert-manager Documentation](https://cert-manager.io/docs/configuration/acme/dns01/cloudflare/)

- [Argo Events Quick Start](https://argoproj.github.io/argo-events/quick_start/)

- [Get GitHub Token](https://argoproj.github.io/argo-events/eventsources/setup/github/)
