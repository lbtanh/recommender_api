#!/bin/sh

kubectl set image deployments/rs-update-ig-engine-deployment rs-update-ig-engine=002663593173.dkr.ecr.us-east-1.amazonaws.com/follou/rs-update-ig-engine:latest
kubectl set image deployments/rs-update-ig-engine-deployment rs-update-ig-engine=002663593173.dkr.ecr.us-east-1.amazonaws.com/follou/rs-update-ig-engine