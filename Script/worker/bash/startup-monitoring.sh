#!/bin/bash

# Make a absolute path instead of relative
abs_path_file_execute=$(realpath "$0")
abs_path_folder_root=$(dirname "$(dirname "$(dirname "$(dirname "$abs_path_file_execute")")")")
abs_path_infrastructure="$abs_path_folder_root/Infrastructure/docker"

# Function to generate configuration
generate_conf() {
    addr=$1
    if [[ $addr != "" ]];then
    # Generate the configuration file for prometheus
    cat << EOF | tee "$abs_path_infrastructure/conf/monitoring/prometheus/prometheus.yml" > /dev/null || echo "The file does not exist" exit 1
# my global config
global:
  scrape_interval: 1s # Set the scrape interval to every 15 seconds. Default is every 1 minute.
  evaluation_interval: 15s # Evaluate rules every 15 seconds. The default is every 1 minute.
  # scrape_timeout is set to the global default (10s).

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - "alertmanager:9093"

# Load rules once and periodically evaluate them according to the global 'evaluation_interval'.
rule_files:
    - "alert.rules.yml"

# A scrape configuration containing exactly one endpoint to scrape:
# Here it's Prometheus itself.
scrape_configs:
  - job_name: 'node_exporter'
    scrape_interval: 5s
    static_configs:
    - targets: ['$addr:9100']
  - job_name: 'cadvisor'
    scrape_interval: 5s
    static_configs:
    - targets: ['$addr:8080']
EOF
    echo "Generating the conf of prometheus successfully"
    # Generate the configuration for alert manager
    cat << EOF | tee "$abs_path_infrastructure/conf/monitoring/alertmanager/alertmanager.yml" > /dev/null || echo "The file does not exist" exit 1
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
    - url: "http://$addr:5000/alerts"
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
if [[ "$1" == "gen" ]];then
   generate_conf "$2"
   exit 0
elif [[ "$1" == "gen-create" ]];then
   generate_conf "$2"
   docker-compose -f "$abs_path_infrastructure/monitoring-compose.yaml" up -d || echo "Something went wrong, check your configuration again or the compose file isn't exist" | exit 1
   echo "Create monitoring compose is completed successfully"
   exit 0
elif [[ "$1" == "create" ]];then
   docker-compose -f "$abs_path_infrastructure/monitoring-compose.yaml" up -d || echo "Something went wrong, check your configuration again or the compose file isn't exist" | exit 1
   echo "Create monitoring compose is completed successfully"
   exit 0
elif [[ "$1" == "destroy" ]];then
   docker-compose -f "$abs_path_infrastructure/monitoring-compose.yaml" down || echo "Something went wrong, the compose file isn't exist" | exit 1
   echo "Destroy monitoring compose is completed successfully"
   exit 0
elif [[ "$1" == "stop" ]];then
   docker-compose -f "$abs_path_infrastructure/monitoring-compose.yaml" stop || echo "Something went wrong, the compose file isn't exist" | exit 1
   echo "Stop monitoring compose is completed successfully"
   exit 0
elif [[ "$1" == "start" ]];then
   docker-compose -f "$abs_path_infrastructure/monitoring-compose.yaml" start || echo "Something went wrong, the compose file isn't exist" | exit 1
   echo "Start monitoring compose is completed successfully"
   exit 0
fi