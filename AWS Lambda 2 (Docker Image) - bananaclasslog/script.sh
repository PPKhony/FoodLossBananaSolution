#!/bin/bash
docker build -t bananaclasslog .
aws ecr create-repository --repository-name bananaclasslog --image-scanning-configuration scanOnPush=true --region us-east-1
docker tag bananaclasslog:latest 637423557159.dkr.ecr.us-east-1.amazonaws.com/bananaclasslog:latest
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 637423557159.dkr.ecr.us-east-1.amazonaws.com
docker push 637423557159.dkr.ecr.us-east-1.amazonaws.com/bananaclasslog:latest