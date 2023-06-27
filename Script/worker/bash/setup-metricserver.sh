#!/bin/bash

abs_path_file_execute=$(realpath "$0")
abs_path_folder_root=$(dirname "$(dirname "$(dirname "$(dirname "$abs_path_file_execute")")")")
abs_path_infrastructure="$abs_path_folder_root/Infrastructure/docker"

whatmetricserver=""
if [[ $1 == "anomalies" ]]; then
    chmod go-w "$abs_path_infrastructure/conf/filebeat/filebeat.yml"
    whatmetricserver="metrics-anomaly-compose.yml"
elif [[ $1 == "autoscale" ]]; then
    whatmetricserver="metrics-autoscale-compose.yml"
elif [[ $1 == "normal" ]]; then
    whatmetricserver="get-data-metric-compose.yaml"
fi

if [[ "$2" == "create" ]]; then
    if [ -z "$(docker network ls | grep monitoring)" ]; then
        docker network create --driver bridge --subnet=172.30.0.0/16 --gateway=172.30.0.1 --scope=local monitoring
    else
        echo "The monitoring network really exist"
    fi
    if [ -z "$(docker network ls | grep data_metric)" ]; then
        docker network create --driver bridge --subnet=172.27.0.0/16 --gateway=172.27.0.1 --scope=local data_metric
    else
        echo "The data_metric network really exist"
    fi
    docker-compose -f "$abs_path_infrastructure/$whatmetricserver" --env-file "$abs_path_folder_root/.env" up -d
    echo "Creating the metric server completed successfully, waiting for minutue to access successfully"
    exit 0
elif [[ "$2" == "destroy" ]]; then
    docker-compose -f "$abs_path_infrastructure/$whatmetricserver" down
    echo "Removing the metric server completed successfully"
    exit 0
elif [[ "$2" == "update" ]]; then
    docker-compose -f "$abs_path_infrastructure/$whatmetricserver" pull
    docker-compose -f "$abs_path_infrastructure/$whatmetricserver" --env-file "$abs_path_folder_root/.env" up -d
    echo "Updating the metric server completed successfully"
    exit 0
elif [[ "$2" == "up" ]]; then
    docker-compose -f "$abs_path_infrastructure/$whatmetricserver" --env-file "$abs_path_folder_root/.env" start
    echo "Starting the metric server completed successfully"
    exit 0
elif [[ "$2" == "down" ]]; then
    docker-compose -f "$abs_path_infrastructure/$whatmetricserver" stop
    echo "Stopping the metric server completed successfully"
    exit 0
else
    echo "Error: Missing argument for option or wrong option, add and retry..."
    exit 1
fi