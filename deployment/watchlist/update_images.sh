#!/bin/sh

kubectl set image deployments/watchlist-engine-deployment watchlist-engine=002663593173.dkr.ecr.us-east-1.amazonaws.com/follou/watchlist-engine:latest
kubectl set image deployments/watchlist-engine-deployment watchlist-engine=002663593173.dkr.ecr.us-east-1.amazonaws.com/follou/watchlist-engine