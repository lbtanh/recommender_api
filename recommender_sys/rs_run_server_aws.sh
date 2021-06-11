#!/bin/sh
#gunicorn -w 30 -b 0.0.0.0:5000 rs_run_server:app
#!/bin/bash

PIDFILE=run/gunicorn.pid
LOGFILE=logs/gunicorn.log
GUNICORN_PORT=${GUNICORN_PORT:-5000}
GUNICORN_HOST=${GUNICORN_HOST:-0.0.0.0}
#VENV=${VENV:-/home/anh_lbt}
NUM_GUNICORN_WORKERS=${NUM_GUNICORN_WORKERS:-20}
TIMEOUT=120

#cd $(dirname $0)

#source ${VENV}/bin/activate
mkdir -p run logs
# kill any existing servers:
# if [[ -e $PIDFILE ]]; then
#     if ! kill -0 $(cat $PIDFILE) 2>/dev/null; then
# 	# process doesn't exist anymore
# 	rm -fv $PIDFILE
#     else
# 	echo -n "killing existing gunicorn ($(cat $PIDFILE))..."
# 	kill $(cat $PIDFILE)
# 	sleep 2
# 	echo 'done!'
#     fi
# fi
echo -n "starting gunicorn..."
gunicorn rs_run_server:app \
	--bind ${GUNICORN_HOST}:${GUNICORN_PORT} \
	--pid=$PIDFILE \
	--log-file=$LOGFILE \
	--workers=$NUM_GUNICORN_WORKERS \
    --timeout=$TIMEOUT
echo 'done!'
