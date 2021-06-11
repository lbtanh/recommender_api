#!/bin/sh
DIRECTORY=$(cd `dirname $0` && pwd)
cd $DIRECTORY
exec python rs_update_ig_server.py