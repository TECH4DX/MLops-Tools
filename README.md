# MLops platform installation guide

## Argo Workflow Install
You need to configure the ArgoWorkflow environment before deploy your own workflows. Fortunately, it is extremely convenient to install ArgoWorkflow based on the cloud-native k8s environment. Make sure you have `kubectl` configured correctly on your machine, use `kubectl apply` command with installation yaml file in `mlops/` folder to install Argo:

```bash
# Create specific namespace for ArgoWorkflow
$ kubectl create ns argo
# Install ArgoWorkflow
$ kubectl apply -f mlops/install.yaml -n argo
```

## Configure Artifact Repository
To run Argo workflows that use artifacts, such as `Mnist` we are running, you must configure and use an artifact repository. Argo supports any S3 compatible artifact repository such as AWS, GCS ( Google Cloud Storage ) and Minio. We all used `GCS` in our examples:
1. Create a bucket and name it `mlops-example-bucket` from the GCP Console (https://console.cloud.google.com/storage/browser).  

2.  Create the Service Account key and store it as a K8s secret:
    ```bash
    $ kubectl create secret generic mlops-bucket-serviceaccount --from-file=serviceAccountKey=<YOUR-SERVICE-ACCOUNT-KEY-file> -n argo
    ```

## Build the docker images

All scripts used for Mnist model training and evaling are in the `mnist/` folder, use `docker build` command to build and tag the image:

```bash
$ cd mnist/docker/
$ docker build -t $DOCKER_REGISTRY/$MY_ORG/mnist-example:$TAG ./
$ docker push $DOCKER_REGISTRY/$MY_ORG/mnist-example:$TAG
```

Scripts used for Mnist serving are in the `mnist-serving` folder:
```bash
$ cd mnist-serving/docker/
$ docker build -t $DOCKER_REGISTRY/$MY_ORG/mnist-serving:$TAG ./
$ docker push $DOCKER_REGISTRY/$MY_ORG/mnist-serving:$TAG
```

Feel free to choose your favorite docker registry(dockerhub, huaweicloud swr...) and create the organization. You may need to login the registry before pushing.


## Replace the image values
After building and pushing the images, specify the image url in the corresponding yaml file, `mnist-train-eval.yaml` in this demo.

```bash 
$ cd mlops
$ vim mnist-train-eval.yaml
# Update the value of 'image' field to your own docker registry url
```

## Setup Mnist workflow
Then all you have to do is set up the resources with kubectl:
```bash
# Setup Mnist workflow:
$ cd mlops
$ kubectl apply -f ./mnist-train-eval.yaml -n argo
```

## Few things to take care of
- TODO