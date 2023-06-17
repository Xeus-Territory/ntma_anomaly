#!/bin/bash

# Absolute path to the directory
abs_path_folder=$(dirname "$(realpath $0)")

clone_visuallizer() {
# Clone project from remote repository
git clone https://github.com/dockersamples/docker-swarm-visualizer.git

# Config port to exposed
cat << EOF | tee "$abs_path_folder/docker-swarm-visualizer/docker-compose.yml" > /dev/null
version: "3"

networks:
  monitoring:
    external: true
services:
  visuallizer:
    container_name: "docker-swarm-visualizer"
    build: .
    image: docker-swarm-visualizer:latest
    deploy:
      resources:
        limits:
          cpus: '0.10'
          memory: 200M
    volumes:
    - "/var/run/docker.sock:/var/run/docker.sock"
    ports:
    - "8081:8080"
    networks:
     - monitoring
EOF
}

# Create the image and build the container for swarm visualization
if [[ "$1" == "create" ]]; then
    clone_visuallizer
    if [ -z "$(docker network ls | grep monitoring)" ]; then
        docker network create --driver bridge --subnet=172.30.0.0/16 --gateway=172.30.0.1 --scope=local monitoring
    else
        echo "The monitoring network really exist"
    fi
    { 
        docker-compose -f docker-swarm-visualizer/docker-compose.yml up -d 
    } || { 
        echo "Error: Cannot create docker-swarm-visualizer" && exit 1 
    }
    echo "Created docker-swarm-visullizer is successfully"
    if [ "$2" == "-n" ]; then
        rm -rf docker-swarm-visualizer
        echo "Remove docker-swarm-visullizer folder is successfully"
        exit 0
    elif [[ "$2" == "" ]]; then
        read -p "Do you want to keep the folder docker-swarm-visualizer[y/n]? " choice
        if [[ $choice == "n" ]]; then
            rm -rf docker-swarm-visualizer
            echo "Remove docker-swarm-visullizer folder is successfully"
            exit 0
        else
            echo "Docker swarm visualizer is worked, enjoy $(echo -e '\xF0\x9F\x8C\x85')"
            exit 0
        fi
    fi
# Destroy the visualizer swarm-visullizer and attach file if it exists
elif [[ "$1" == "destroy" ]]; then
    if [[ -d "$abs_path_folder/docker-swarm-visualizer" ]]; then
        docker-compose -f "$abs_path_folder/docker-swarm-visualizer/docker-compose.yml" down
        rm -rf "$abs_path_folder/docker-swarm-visualizer"
        if [[ "$2" == "-y" ]]; then
            exit 1
        fi
        read -p "Do you want to keep the docker-swarm-visualizer image [y/n]? " choice
        if [[ $choice == "n" ]]; then
            {
                docker rmi -f docker-swarm-visualizer 
            } || {
                echo "Error: Failed to remove image docker-swarm-visualizer" && exit 1
            }
        fi  
        echo "Destroy successfully docker-swarm-visualizer"
        exit 0
    else
        docker rm -f docker-swarm-visualizer || (echo "Error: Failed to remove container docker-swarm-visualizer" | exit 1)
        if [[ "$2" == "-y" ]]; then
            exit 0
        fi
        read -p "Do you want to keep the docker-swarm-visualizer image [y/n]? " choice
        if [[ $choice == "n" ]]; then        
            {
                docker rmi -f docker-swarm-visualizer 
            } || {
                echo "Error: Failed to remove image docker-swarm-visualizer" && exit 1
            }
        fi
        echo "Successfully removed docker-swarm-visualizer"
    fi
# Error when not input the action
elif [[ "$1" == "" ]]; then
    echo "Error: No option specified for docker-swarm-visualizer, please specify and try again !!!"
    exit 1
fi
