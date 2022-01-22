#! /bin/bash

SECRET=$(kubectl get sa argo-server -n argo -o=jsonpath='{.secrets[0].name}')
ARGO_TOKEN="Bearer $(kubectl get secret $SECRET -n argo -o=jsonpath='{.data.token}' | base64 --decode)"
echo $ARGO_TOKEN
#output: Bearer ZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNkltS...
