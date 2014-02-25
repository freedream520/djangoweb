#!/usr/bin/bash

UWSGI_PID_FILE="$(pwd)/uwsgi.pid"
UWSGI_INI_FILE="$(pwd)/uwsgi.ini"
UWSGI_MASTER_PID=$(ps -ef| grep uwsgi | awk '$3 == 1 {print $2}')

if ! [ "x$UWSGI_MASTER_PID" == "x" ]; then

	# create pid file
	if ! [ -f "$UWSGI_PID_FILE" ]; then
		touch $UWSGI_PID_FILE
	fi
	
	# check pid
	pid=$(cat ${UWSGI_PID_FILE})
	if ! [ "x${pid}" == "x${UWSGI_MASTER_PID}" ]; then
		echo ${UWSGI_MASTER_PID} > "${UWSGI_PID_FILE}"
	fi

	kill -HUP `cat ${UWSGI_PID_FILE}`
else
	uwsgi ${UWSGI_INI_FILE}
fi


