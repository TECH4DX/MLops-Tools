## **Workflows** 工作流 

Workflows is a container-native workflow engine for orchestrating parallel jobs on Kubernetes.We build it on top of Argo Workflows, which is implemented as a Kubernetes CRD (Custom Resource Definition).

工作流是一个容器原生的工作流引擎，用于在Kubernetes上编排并行作业。我们在Argo Workflow之上构建它，它被作为Kubernetes CRD实现的 (自定义资源定义).

## Argo Workflow Install安装Argo Workflow

You need to configure the ArgoWorkflow environment before deploy your own workflows. Fortunately, it is extremely convenient to install ArgoWorkflow based on the cloud-native k8s environment. Make sure you have `kubectl` configured correctly on your machine, use `kubectl apply` command with installation yaml file in `workflows/` folder to install Argo:

你需要在部署自己的工作流之前配置 Argo Workflow环境。幸好，基于云原生k8s环境安装Argo Workflow非常方便。确保您在您的机器上正确配置了 `kubectl` ，使用在 `workflows/`文件夹中带有安装yaml文件的 `kubectl apply` 按键去安装Argo:

```
# Create specific namespace for ArgoWorkflow 
$ kubectl create ns argo  kubectl 
# Install ArgoWorkflow  
$ kubectl apply -f workflows/install.yaml -n argo
```

**Optional:** Download the latest Argo CLI from official [releases page](https://github.com/argoproj/argo-workflows/releases/latest) which includes the guide on setting up.

可选：从官方发布页面下载最新的Argo CLI，其中包括设置指南。

## Configure Artifact Repository  配置Artifact仓库

To run Argo workflows that use artifacts, such as `Mnist` we are running, you must configure and use an artifact repository. Argo supports any S3 compatible artifact repository such as AWS, GCS ( Google Cloud Storage ) and Minio. We all used `GCS` in our examples:

为了运行使用artifacts的Argo workflows，如我们正在运行的`Mnist` ，必须配置和使用一个artifact repository。

Argo支持任何与S3兼容的artifact repository ，如AWS、GCS（谷歌云存储）和 Minio。我们在示例中都使用了 `GCS` ：

1. Create a bucket and name it `mlops-example-bucket` from the GCP Console 从 GCP 控制台创建一个存储桶并将其命名为 mlops-example-bucket  (<https://console.cloud.google.com/storage/browser>).

2. Create the Service Account key and store it as a K8s secret:创建服务帐户密钥并将其存储为 K8s 机密：

   

   ```
   # Create specific namespace for Mnist Demo 为 Mnist Demo 
   $ kubectl create ns mnist-demo  kubectl 
   # Create secret for GCS used by Mnist workflows  
   $ kubectl create secret generic mlops-bucket-serviceaccount --from-file=serviceAccountKey=<YOUR-SERVICE-ACCOUNT-KEY-file> -n mnist-demo
   ```

## Create Service Account for Argo Workflows 为Argo Workflows创建服务账户

To access cluster resources, such as pods and workflows contronller, you should create a new service account with proper authorization. 

要访问集群资源，如pods和workflows 控制器，您应该创新一个具体适当授权的新的服务账户

```
$ kubectl create -f workflows/create-serviceaccounts.yaml -n mnist-demo
```

## Mnist Example (Optional) Mnist 示例（可选） 

### **Build Images**  构建图像

All scripts used for Mnist model training and evaling are in the `mnist/` folder, use `docker build` command to build and tag the image:

用于Mnist 模型训练和评估的所有脚本都在`mnist/`文件夹，使用`docker build` 命令构建和标记图像

```
$ cd mnist/docker/
$ docker build -t $DOCKER_REGISTRY/$MY_ORG/mnist-example:$TAG ./
$ docker push $DOCKER_REGISTRY/$MY_ORG/mnist-example:$TAG
```

Scripts used for Mnist serving are in the `mnist-serving` folder: 用到Mnist服务的脚本在 `mnist-serving` 文件夹中：

```
$ cd mnist-serving/docker/
$ docker build -t $DOCKER_REGISTRY/$MY_ORG/mnist-serving:$TAG ./
$ docker push $DOCKER_REGISTRY/$MY_ORG/mnist-serving:$TAG
```

Feel free to choose your favorite docker registry(dockerhub, huaweicloud swr...) and create the organization. You may need to login the registry before pushing.

自由地选择您 最喜欢的docker注册中心（dockerhub、huaweicloud swr...）并创建组织。

### **Replace the image values**替换图像值

After building and pushing the images, specify the image url in the corresponding yaml file, `mnist-train-eval.yaml` in this demo. 

构建并推送图像后，在对应的yaml文件中指定图像url，`mnist-train-eval.yaml`在这个演示里。

```
$ cd workflows
$ vim examples/mnist-train-eval.yaml
# Update the value of 'image' field to your own docker registry url
```

### **Setup Mnist workflow**设置 Mnist Workflow

Then all you have to do is set up the resources with kubectl: 

然后你所要做的就是使用 kubectl 设置资源： 

```
# Setup Mnist workflow:
$ cd workflows
$ kubectl apply -f ./examples/mnist-train-eval.yaml -n mnist-demo
```

**NOTE:** Once all three steps in workflow `mnist-train-eval` passed, you can visit the mnist website with url `https://MASTER_NODE_IP:9003` . Draw a digit and test it.

**注意:** 一旦工作流 `mnist-train-eval` 所有的三个步骤都通过，您可以使用 url 访问 mnist 网站 `https://MASTER_NODE_IP:9003` . 

## **Events**

Events is an event-driven workflow automation framework for Kubernetes which helps you trigger K8s objects, Argo Workflows, Serverless workloads, etc. on events from a variety of sources like webhooks, S3, schedules, messaging queues, gcp pubsub, sns, sqs, etc.

Events是一个用于Kubernetes的事件驱动的工作流自动框架，它可以帮助触发K8s对象，Argo Workflows，无服务器工作负载等来自各种来源的事件，如 webhooks, S3, schedules, messaging queues, gcp pubsub, sns, sqs等。

## Argo Events Install安装Argo Events

Argo Events is an event-driven workflow automation framework for Kubernetes which helps you trigger K8s objects, Argo Workflows, Serverless workloads, etc. on events from a variety of sources like webhooks, S3, schedules, messaging queues, gcp pubsub, sns, sqs, etc.

Argo Events是一个用于Kubernetes的事件驱动的工作流自动框架，它可以帮助触发K8s对象，Argo Workflows，无服务器工作负载等来自各种来源的事件，如 webhooks, S3, schedules, messaging queues, gcp pubsub, sns, sqs等。

```
# Create specific namespace for argo events
$ kubectl create namespace argo-events

# Deploy Argo Events, SA, ClusterRoles, Sensor Controller, EventBus Controller and EventSource Controller.
# Cluster-wide Installation
$ kubectl apply -f events/install.yaml
# Or Namespace Installation
$ kubectl apply -f events/namespace-install.yaml
```

## Create Service Account for Argo Events为Argo Events创建服务账户

To make the Sensors be able to trigger Workflows, a Service Account with RBAC settings is required (assume you run the examples in the namespace argo-events).

为了使传感器能够触发工作流，需要一个具有 RBAC设置的服务账户（假设您在命名空间 argo-events 中运行示例）。

```
$ kubectl apply -f events/create-serviceaccount.yaml -n argo-events
```

## Webhook Example of Argo Events (Optional)

## Argo Events的 Webhook示例

We are going to set up a sensor and event-source for webhook. The goal is to trigger an Argo workflow upon a HTTP Post request.

我们将为 webhook 设置传感器和事件源。目标是根据 HTTP Post 请求触发 Argo workflow。

- Set up the eventbus.

  ```
  $ kubectl apply -f events/examples/eventbus_native.yaml -n argo-events
  ```

- Create the webhook event source.

  ```
  $ kubectl apply -f events/examples/eventsource_webhook.yaml -n argo-events
  ```

- Create the webhook sensor.

  ```
  $ kubectl apply -f events/examples/sensor_webhook.yaml -n argo-events
  ```

If the commands are executed successfully, the eventbus, event-source and sensor pods will get created. You will also notice that a service is created for the event-source.

如果成功执行命令，将创建事件总线、事件源和传感器pods。 您还会注意到为事件源创建的一个服务。 

- Use either Curl or Postman to send a post request to the <http://localhost:9100/example>.

  ```
  $ curl -d '{"message":"this is my first webhook"}' -H "Content-Type: application/json" -X POST http://localhost:9100/example
  ```

- Now, you should see an Argo workflow being created.

  ```
  $ kubectl get wf -n argo-events
  ```

- Make sure the workflow pod ran successfully. You will see the message printed in the workflow logs

  ```
   _____________________________
   < this is my first webhook >
  ------------------------------
      \
      \
      \
                      ##        .
              ## ## ##       ==
          ## ## ## ##      ===
      /""""""""""""""""___/ ===
  ~~~ {~~ ~~~~ ~~~ ~~~~ ~~ ~ /  ===- ~~~
      \______ o          __/
          \    \        __/
          \____\______/
  ```

## **CD**

We build CD on top of ArgoCD, which is a declarative, GitOps continuous delivery tool for Kubernetes.

我们在 ArgoCD 之上构建 CD，ArgoCD 是一种用于 Kubernetes 的声明性 GitOps 持续交付工具。

## Argo CD Install

We will create a new namespace, argocd, where Argo CD services and application resources will live.

我们将创建一个新的命名空间 argocd，Argo CD 服务和应用程序资源将存放在其中。

```
$ kubectl create namespace argocd
$ kubectl apply -f cd/install.yaml -n argocd
```

## Login via UI

The initial password for the `admin` account is auto-generated and stored as clear text in the field `password` in a secret named `argocd-initial-admin-secret` in your Argo CD installation namespace. You can simply retrieve this password using `kubectl`:  

 `admin` 帐户的初始密码是自动生成的，并以明文形式存储在 Argo CD 安装命名空间中名为 `argocd-initial-admin-secret`  的密码字段中。您可以使用  `kubectl`简单地检索此密码：



```
$ kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
```

Open a browser to the Argo CD external UI, and login by visiting the IP/hostname(*https://MASTER_NODE_IP:2747*) in a browser.

打开浏览器到 Argo CD 外部 UI，并通过在浏览器中访问 IP/主机名(*https://MASTER_NODE_IP:2747*)  登录。

## Few things to take care of 注意事项

- The current default setting of Argo needs to use the token to login, you may need to generate a token with shell script we provided:

  Argo当前默认设置需要使用token登录，您可能需要使用我们提供的shell脚本生成token：

  ```
  $ ./workflows/gen_token.sh
  # Copy the output starting with 'Bearer' to the token box of the Argo login interface (https://MASTER_NODE_IP:2746)
  # Now you can see all the workflows in argo namespace on https://MASTER_NODE_IP:2746/workflows/argo web.
  ```

  Argo url: `https://MASTER_NODE_IP:2746`

- Before you deploy the public network service, please make sure that the firewall policy of your cloud server allows outgoing communication on the required port, such as port `2746` and `9003` .

  在部署公网服务之前，请确保您的云服务器的防火墙策略允许在所需端口上进行传出通信，例如端口  `2746`  和  `9003`  。

- See more technical details in the [Argo Workflows official document](https://argoproj.github.io/argo-workflows/) and [Argo Events official document](https://argoproj.github.io/argo-events/).

  更多技术细节，请查看 [Argo Workflows official document](https://argoproj.github.io/argo-workflows/)和[Argo Events official document](https://argoproj.github.io/argo-events/)。

- See more examples in [Argo Workflows Github Repository](https://github.com/argoproj/argo-workflows/tree/master/examples) and [Argo Events Github Repository](https://github.com/argoproj/argo-events/tree/master/examples).

  更多示例，请查看[Argo Workflows Github Repository](https://github.com/argoproj/argo-workflows/tree/master/examples)和[Argo Events Github Repository](https://github.com/argoproj/argo-events/tree/master/examples) 。
