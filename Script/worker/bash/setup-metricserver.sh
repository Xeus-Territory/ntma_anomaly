#!/bin/bash

abs_path_file_execute=$(realpath "$0")
abs_path_folder_root=$(dirname "$(dirname "$(dirname "$(dirname "$abs_path_file_execute")")")")
abs_path_infrastructure="$abs_path_folder_root/Infrastructure/docker"

if [[ "$1" == "create" ]]; then
    docker-compose -f "$abs_path_infrastructure/get-data-metric-compose.yaml" up -d
    echo "Creating the metric server completed successfully, waiting for minutue to access successfully"
    exit 0
elif [[ "$1" == "destroy" ]]; then
    docker-compose -f "$abs_path_infrastructure/get-data-metric-compose.yaml" down
    echo "Removing the metric server completed successfully"
    exit 0
elif [[ "$1" == "update" ]]; then
    docker-compose -f "$abs_path_infrastructure/get-data-metric-compose.yaml" pull
    docker-compose -f "$abs_path_infrastructure/get-data-metric-compose.yaml" up -d
    echo "Updating the metric server completed successfully"
    exit 0
elif [[ "$1" == "up" ]]; then
    docker-compose -f "$abs_path_infrastructure/get-data-metric-compose.yaml" start
    echo "Starting the metric server completed successfully"
    exit 0
elif [[ "$1" == "down" ]]; then
    docker-compose -f "$abs_path_infrastructure/get-data-metric-compose.yaml" stop
    echo "Stopping the metric server completed successfully"
    exit 0
else
    echo "Error: Missing argument for option or wrong option, add and retry..."
    exit 1
fi