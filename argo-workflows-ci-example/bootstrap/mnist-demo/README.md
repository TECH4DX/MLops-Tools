# Demo

```shell
kubectl create -f ns.yaml
kubectl create -f secret.yaml
kubectl create -f create-serviceaccounts.yaml -n mnist-demo
kubectl create -f mnist-train-eval.yaml -n mnist-demo
```
