#!/bin/sh

SOURCE_PATH=`pwd`
DOCKER_IMG_NAME='watchlist-engine'
echo ${SOURCE_PATH}
echo ${DOCKER_IMG_NAME}
branch=$1
version=$2

# Clear all old tar file
rm -rf *tar.gz
cd ../../../
git archive ${branch} --format=tar.gz -o ${SOURCE_PATH}/sw_follou_recommendation.tar.gz ./recommender_api
cd ${SOURCE_PATH}

export DOCKER=follou/${DOCKER_IMG_NAME}
docker build -t ${DOCKER}:${version} .