#!/bin/bash

APP_FILE="app.py"
PID_FILE="app.pid"

function start_app() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "Application is already running with PID $(cat "$PID_FILE")."
        exit 1
    fi

    echo "Starting Flask application..."
    nohup python3 "$APP_FILE" > app.log 2>&1 &
    echo $! > "$PID_FILE"
    echo "Application started with PID $(cat "$PID_FILE")."
}

function stop_app() {
    if [ ! -f "$PID_FILE" ] || ! kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "Application is not running."
        exit 1
    fi

    echo "Stopping Flask application..."
    kill $(cat "$PID_FILE")
    rm -f "$PID_FILE"
    echo "Application stopped."
}

case "$1" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        exit 1
        ;;
esac
