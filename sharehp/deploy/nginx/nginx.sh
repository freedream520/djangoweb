#!/bin/bash

NGINX_CONFIG_FILE="$(pwd)/nginx.conf"
NGINX_PID_FILE="$(pwd)/nginx.pid"

if ! nginx -tc "$NGINX_CONFIG_FILE" ; then
	echo "nginx config error!"
	exit -1
fi

NGINX_MASTER_PID=$(ps -ef| grep nginx | awk '$3 == 1 {print $2}')

if ! [ "x$NGINX_MASTER_PID" == "x" ]; then

	# create pid file
	if ! [ -f "$NGINX_PID_FILE" ]; then
		touch $NGINX_PID_FILE
	fi
	
	# check pid
	pid=$(cat ${NGINX_PID_FILE})
	if ! [ "x${pid}" == "x${NGINX_MASTER_PID}" ]; then
		echo ${NGINX_MASTER_PID} > "${NGINX_PID_FILE}"
	fi

	nginx -s reload -c  "$NGINX_CONFIG_FILE"
else
	nginx -c  "$NGINX_CONFIG_FILE"
fi
	



