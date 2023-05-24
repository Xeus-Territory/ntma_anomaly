#!/bin/bash

if [[ "$2" != "" ]]; then
    if [[ "$1" == "agent" ]]; then
        docker build -f dockerfile.agent -t agent-script:"$2" .
        echo "Build successfully"
        exit 0
    elif [[ "$1" == "nginx" ]]; then
        cd Infrastructure/docker/ || exit 1
        docker build -f dockerfile.nginx -t nginx-rebuild:"$2" .
        echo "Build successfully"
        exit 0
    elif [[ "$1" == "app" ]]; then
        cd Infrastructure/docker/ || exit 1
        docker build -f dockerfile.app -t application:"$2" .
        echo "Build successfully"
        exit 0
    elif [[ "$1" == "" ]]; then
        echo "No image specified for build, choose again."
        exit 1
    fi
else
    echo "No tag specified for build, cannot be latest is applied, try again."
    exit 1
fi
