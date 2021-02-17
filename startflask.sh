#!/usr/bin/env bash
pyapp=$1
if [[ $pyapp == "" ]];
then
    echo "Missing file name."
    echo "Usage:"
    echo "./startflask.sh example.py"
else
    echo "Start flask with "$pyapp
    exec `export FLASK_APP=$pyapp`
#Debug mode
    exec `export FLASK_DEBUG="0"`
#Turn on development function FLASK_ENV="development"
    exec `export FLASK_ENV=""`
    exec `flask run --host=0.0.0.0`
fi
