#!/bin/bash

name=$1 

## Get the name of the service base on container name
service_name=$(echo "$name" | cut -d "." -f 1)

## Current number replication is running
replica_really_exist=$(docker service ls | grep "$service_name" | awk '{print $4}' | cut -d "/" -f 2)

## Scale up or scale down the service
if [[ $2 == "up" ]]; then
    docker service scale "$service_name"=$(("$replica_really_exist" + $3)) > /dev/null
    exit 0
else
    if [[ $(("$replica_really_exist")) -gt 1 ]]; then
        docker service scale "$service_name"=$(("$replica_really_exist" - $3)) > /dev/null
        exit 0
    else
        exit 1
    fi
fi
