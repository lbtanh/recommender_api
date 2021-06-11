#!/bin/sh

DOCKER_REPO=002663593173.dkr.ecr.us-east-1.amazonaws.com
DOCKER=follou/influencer-recommandation
echo ${DOCKER_REPO}/${DOCKER};
docker tag ${DOCKER}:latest ${DOCKER_REPO}/${DOCKER}:latest
docker push ${DOCKER_REPO}/${DOCKER}:latest