#!/bin/bash

# Make a absolute path instead of relative
abs_path_file_execute=$(realpath "$0")
abs_path_folder_root=$(dirname "$(dirname "$(dirname "$(dirname "$abs_path_file_execute")")")")
abs_path_infrastructure="$abs_path_folder_root/Infrastructure/docker"

# Function to generate configuration
generate_conf() {
  addr=$1
  node=$2
  api=$3
  
  if [[ $addr != "" && $node != "" && $api != "" ]]; then
    # Generate the configuration for default prometheus
    cat << EOF | tee "$abs_path_infrastructure/conf/monitoring/prometheus/target/cadvisor.json" > /dev/null || echo "ERROR: The file does not exist"
[
  {
    "labels": {
      "job": "cadvisor"
    },
    "targets": [
      "$addr:8080"
    ]
  }
]
EOF
    cat << EOF | tee "$abs_path_infrastructure/conf/monitoring/prometheus/target/node-exporter.json" > /dev/null || echo "ERROR: The file does not exist"
[
  {
    "labels": {
      "job": "cadvisor"
    },
    "targets": [
      "$addr:9100"
    ]
  }
]
EOF
    cat << EOF | tee "$abs_path_infrastructure/conf/monitoring/prometheus/target/nginx-exporter.json" > /dev/null || echo "ERROR: The file does not exist"
[
  {
    "labels": {
      "job": "cadvisor"
    },
    "targets": [
      "$node:9113"
    ]
  }
]
EOF
    # Generate the configuration for alert manager
    cat <<EOF | tee "$abs_path_infrastructure/conf/monitoring/alertmanager/alertmanager.yml" > /dev/null || echo "ERROR: The file does not exist"
global:
  resolve_timeout: 1m

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 30s
  repeat_interval: 10s
  receiver: 'webhook_python'

  routes:
    - receiver: 'webhook_python'

receivers:
  - name: webhook_python
    webhook_configs:
    - url: "$api:5000"
      send_resolved: true
      
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
EOF
    echo "Generating the conf of alertmanager successfully"
  else
    echo "Not input the [ip addr or dns] for generating configuration"
  fi
}

# Generate the configuration file
if [[ "$1" == "gen" ]]; then
  generate_conf "$2" "$3" "$4"
  exit 0

# Generate the configuration file and create monitoring group
elif [[ "$1" == "gen-create" ]]; then
  generate_conf "$2" "$3" "$4"
  if [ -z "$(docker network ls | grep monitoring)" ]; then
    docker network create --driver bridge --subnet=172.30.0.0/16 --gateway=172.30.0.1 --scope=local monitoring
  else
    echo "The monitoring network really exist"
  fi
  {
    docker-compose -f "$abs_path_infrastructure/monitoring-compose.yaml" up -d
  } || {
    echo "Something went wrong, check your configuration again or the compose file isn't exist" && exit 1
  }
  echo "Create monitoring compose is completed successfully"
  exit 0

# Not need to generate a new config, just create monitoring group
elif [[ "$1" == "create" ]]; then
  if [ -z "$(docker network ls | grep monitoring)" ]; then
    docker network create --driver bridge --subnet=172.30.0.0/16 --gateway=172.30.0.1 --scope=local monitoring
  else
    echo "The monitoring network really exist"
  fi
  {
    docker-compose -f "$abs_path_infrastructure/monitoring-compose.yaml" up -d
  } || {
    echo "Something went wrong, check your configuration again or the compose file isn't exist" && exit 1
  }
  echo "Create monitoring compose is completed successfully"
  exit 0

# Destroy the monitoring group include network and visuallizer
elif [[ "$1" == "destroy" ]]; then
  {
    docker-compose -f "$abs_path_infrastructure/monitoring-compose.yaml" down
  } || {
    echo "Something went wrong, check your configuration again or the compose file isn't exist" && exit 1
  }
  {
    docker network rm monitoring
  } || {
    echo "Something went wrong, check your configuration again or the compose" && exit 1
  }
  echo "Destroy monitoring compose is completed successfully"
  exit 0

# Turn off the monitoring group
elif [[ "$1" == "down" ]]; then
  {
    docker-compose -f "$abs_path_infrastructure/monitoring-compose.yaml" stop 
  } || {
    echo "Something went wrong, check your configuration again or the compose file isn't exist" && exit 1 
  }
  echo "Stop monitoring compose is completed successfully"
  exit 0

# Turn on the monitoring group
elif [[ "$1" == "up" ]]; then
  { 
    docker-compose -f "$abs_path_infrastructure/monitoring-compose.yaml" start 
  } || {
    echo "Something went wrong, check your configuration again or the compose file isn't exist" && exit 1 
  }
  echo "Start monitoring compose is completed successfully"
  exit 0
else
    echo "Error: Missing argument for option or wrong option, add and retry..."
    exit 1
fi
