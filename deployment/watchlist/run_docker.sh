#!/bin/sh

docker run \
    -d \
    --rm \
    -e "CONFIG_SOURCE=local_config" \
    follou/watchlist-engine:v1