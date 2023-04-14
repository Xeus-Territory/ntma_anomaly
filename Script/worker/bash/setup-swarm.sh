#!/bin/bash

# Make a absolute path instead of relative
abs_path_file_execute=$(realpath "$0")
abs_path_folder_root=$(dirname "$(dirname "$(dirname "$(dirname "$abs_path_file_execute")")")")
abs_path_application="$abs_path_folder_root/Application"
abs_path_infrastructure="$abs_path_folder_root/Infrastructure/docker"

opt="$1"
if [[ $opt == "create" ]]; then
    # Setup the environment for swarm 
    # 1. Check if swarm is running
    if [ "$(docker info --format '{{.Swarm.LocalNodeState}}')" == "active" ]; then
        echo "Swarm is running"
    else
        echo "Swarm is not running"
        docker swarm init --advertise-addr "$2" 1> /dev/null || echo "Choose the valid network for swarm, detect more NIC instances"
        docker swarm join-token worker | tr -d "\n" | cut -d ":" -f 2-3 > ./temp/output
        echo "Swarm is created successfully and check the token at ./temp/output"
    fi

    # 2. Setup the network for swarm
    if [ -z "$(docker network ls | grep application)" ]; then
        docker network create --driver=overlay --subnet=172.21.0.0/16 \
        --gateway=172.21.0.1 --scope=swarm application 1> /dev/null
        echo "Network is created successfully"
    else
        echo "Network is really exist"
    fi

    # 3. Join container into swarm
    cd "$abs_path_application" || exit
    docker stack deploy -c docker-compose.yaml todo
    cd "$abs_path_infrastructure" || exit
    docker stack deploy -c docker-compose.yaml todo
    exit 0
    
elif [[ $opt == "destroy" ]]; then
    # 1. Remove stack from swarm
    if [ ! -z "$(docker stack ls | grep todo)" ]; then
        docker stack rm todo 1> /dev/null
        echo "Remove stack from swarm"
    else
        echo "the stack in not really exist"
        exit 1
    fi
    # 2. Remove network
        docker network rm application 1>/dev/null
        echo "Network is deleted successfully"
    # 3. Leave Swarm
        docker swarm leave --force
        exit 0
elif [[ $opt == "down" ]]; then
    # Turn down the application on swarm
    docker stack rm todo 1> /dev/null
    echo "Application on swarm is turned down successfully"
    exit 0
elif [[ $opt == "up" ]]; then
    # Start the application
    cd "$abs_path_application" || exit
    docker stack deploy -c docker-compose.yaml todo
    cd "$abs_path_infrastructure" || exit
    docker stack deploy -c docker-compose.yaml todo
    echo "Application on swarm is started successfully"
    exit 0
else
    echo "Not have options, choose for doing"
    exit 1
fi