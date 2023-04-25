#!/bin/bash

# Make a absolute path instead of relative
abs_path_file_execute=$(realpath "$0")
abs_path_folder_root=$(dirname "$(dirname "$(dirname "$(dirname "$abs_path_file_execute")")")")
abs_path_infrastructure="$abs_path_folder_root/Infrastructure/docker"

# Function to generate configuration
generate_conf() {
  addr=$1
  if [[ $addr != "" ]]; then
    # Generate the configuration for alert manager
    cat <<EOF | tee "$abs_path_infrastructure/conf/monitoring/alertmanager/alertmanager.yml" >/dev/null || echo "The file does not exist"
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
    - url: "$addr"
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
  generate_conf "$2"
  exit 0
# Generate the configuration file and create monitoring group
elif [[ "$1" == "gen-create" ]]; then
  generate_conf "$2"
  {
    docker network create --driver bridge --subnet=172.30.0.0/16 --gateway=172.30.0.1 --scope=local monitoring
  } || {
    echo "Error when generating network" && exit 1
  }
  bash -c "./setup-swarm-visuallizer.sh create -n"
  {
    docker-compose -f "$abs_path_infrastructure/monitoring-compose.yaml" up -d
  } || {
    echo "Something went wrong, check your configuration again or the compose file isn't exist" && exit 1
  }
  echo "Create monitoring compose is completed successfully"
  exit 0
# Not need to generate a new config, just create monitoring group
elif [[ "$1" == "create" ]]; then
  {
    docker network create --driver bridge --subnet=172.30.0.0/16 --gateway=172.30.0.1 --scope=local monitoring
  } || {
    echo "Error when generating network" && exit 1
  }
  bash -c "./setup-swarm-visuallizer.sh create -n"
  {
    docker-compose -f "$abs_path_infrastructure/monitoring-compose.yaml" up -d
  } || {
    echo "Something went wrong, check your configuration again or the compose file isn't exist" && exit 1
  }
  echo "Create monitoring compose is completed successfully"
  exit 0
# Destroy the monitoring group include network and visuallizer
elif [[ "$1" == "destroy" ]]; then
  bash -c "./setup-swarm-visuallizer.sh destroy -y"
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
  bash -c "./setup-swarm-visuallizer.sh destroy -y"
  {
    docker-compose -f "$abs_path_infrastructure/monitoring-compose.yaml" stop 
  } || {
    echo "Something went wrong, check your configuration again or the compose file isn't exist" && exit 1 
  }
  echo "Stop monitoring compose is completed successfully"
  exit 0
# Turn on the monitoring group
elif [[ "$1" == "up" ]]; then
  bash -c "./setup-swarm-visuallizer.sh create -n"
  { 
    docker-compose -f "$abs_path_infrastructure/monitoring-compose.yaml" start 
  } || {
    echo "Something went wrong, check your configuration again or the compose file isn't exist" && exit 1 
  }
  echo "Start monitoring compose is completed successfully"
  exit 0
fi