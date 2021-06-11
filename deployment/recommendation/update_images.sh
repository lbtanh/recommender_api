#!/bin/sh

kubectl set image deployments/influencer-recommendation-deployment influencer-recommendation=002663593173.dkr.ecr.us-east-1.amazonaws.com/follou/influencer-recommandation:latest
kubectl set image deployments/influencer-recommendation-deployment influencer-recommendation=002663593173.dkr.ecr.us-east-1.amazonaws.com/follou/influencer-recommandation