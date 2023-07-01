#! /bin/bash

abs_path_file_execute=$(dirname "$(realpath "$0")")
abs_path_folder_script="$abs_path_file_execute/Script/worker/bash"

arr=("$@")
for i in "${arr[@]}";
    do
        if [[ $(echo "${arr[@]: -1}") == "up" ]]; then
            if [ $i == "all" ]; then
                bash -c "$abs_path_folder_script/setup-swarm.sh up" || exit 1
                bash -c "$abs_path_folder_script/setup-monitoring.sh up" ||  exit 1
                bash -c "$abs_path_folder_script/setup-worker.sh ai up" || exit 1
                bash -c "$abs_path_folder_script/setup-metricserver.sh anomalies up" || exit 1
                bash -c "$abs_path_folder_script/setup-metricserver.sh autoscale up" || exit 1
            fi
            if [ $i == "swarm" ]; then
                bash -c "$abs_path_folder_script/setup-swarm.sh up"
            fi
            if [ $i == "worker" ]; then
                bash -c "$abs_path_folder_script/setup-worker.sh ai up"
            fi
            if [ $i == "monitoring" ]; then
                bash -c "$abs_path_folder_script/setup-monitoring.sh up"
            fi
            if [ $i == "anomalies" ]; then
                bash -c "$abs_path_folder_script/setup-metricserver.sh anomalies up"
            fi
            if [ $i == "autoscale" ]; then
                bash -c "$abs_path_folder_script/setup-metricserver.sh autoscale up"
            fi
            if [ $i == "visuallizer" ]; then
                bash -c "$abs_path_folder_script/setup-swarm-visuallizer.sh up"
            fi
            if [ $i == "cadvisor" ]; then
                bash -c "$abs_path_folder_script/setup-cadvisor.sh up"
            fi
            if [ $i == "node-exporter" ]; then
                bash -c "$abs_path_folder_script/setup-node-exporter.sh up"
            fi                
        fi
        if [[ $(echo "${arr[@]: -1}") == "create" ]]; then
            if [ $i == "all" ]; then
                bash -c "$abs_path_folder_script/setup-swarm.sh create" || exit 1
                bash -c "$abs_path_folder_script/setup-monitoring.sh create" ||  exit 1
                bash -c "$abs_path_folder_script/setup-worker.sh ai up" || exit 1
                bash -c "$abs_path_folder_script/setup-metricserver.sh anomalies create" || exit 1
                bash -c "$abs_path_folder_script/setup-metricserver.sh autoscale create" || exit 1
            fi
            if [ $i == "swarm" ]; then
                bash -c "$abs_path_folder_script/setup-swarm.sh create"
            fi
            if [ $i == "worker" ]; then
                bash -c "$abs_path_folder_script/setup-worker.sh ai up"
            fi
            if [ $i == "monitoring" ]; then
                bash -c "$abs_path_folder_script/setup-monitoring.sh create"
            fi
            if [ $i == "anomalies" ]; then
                bash -c "$abs_path_folder_script/setup-metricserver.sh anomalies create"
            fi
            if [ $i == "autoscale" ]; then
                bash -c "$abs_path_folder_script/setup-metricserver.sh autoscale create"
            fi
            if [ $i == "cadvisor" ]; then
                bash -c "$abs_path_folder_script/setup-cadvisor.sh create 0.47.0"
            fi
            if [ $i == "node-exporter" ]; then
                bash -c "$abs_path_folder_script/setup-node-exporter.sh create 1.5.0"
            fi
            if [ $i == "visuallizer" ]; then
                bash -c "$abs_path_folder_script/setup-swarm-visuallizer.sh create -n"
            fi                
        fi
        if [[ $(echo "${arr[@]: -1}") == "down" ]]; then
            if [ $i == "all" ]; then
                bash -c "$abs_path_folder_script/setup-swarm.sh down" || exit 1
                bash -c "$abs_path_folder_script/setup-monitoring.sh down" ||  exit 1
                bash -c "$abs_path_folder_script/setup-worker.sh ai down" || exit 1
                bash -c "$abs_path_folder_script/setup-metricserver.sh anomalies down" || exit 1
                bash -c "$abs_path_folder_script/setup-metricserver.sh autoscale down" || exit 1
            fi
            if [ $i == "swarm" ]; then
                bash -c "$abs_path_folder_script/setup-swarm.sh down"
            fi
            if [ $i == "worker" ]; then
                bash -c "$abs_path_folder_script/setup-worker.sh ai down"
            fi
            if [ $i == "monitoring" ]; then
                bash -c "$abs_path_folder_script/setup-monitoring.sh down"
            fi
            if [ $i == "anomalies" ]; then
                bash -c "$abs_path_folder_script/setup-metricserver.sh anomalies down"
            fi
            if [ $i == "autoscale" ]; then
                bash -c "$abs_path_folder_script/setup-metricserver.sh autoscale down"
            fi
            if [ $i == "cadvisor" ]; then
                bash -c "$abs_path_folder_script/setup-cadvisor.sh down"
            fi
            if [ $i == "node-exporter" ]; then
                bash -c "$abs_path_folder_script/setup-node-exporter.sh down"
            fi
            if [ $i == "visuallizer" ]; then
                bash -c "$abs_path_folder_script/setup-swarm-visuallizer.sh down"
            fi                
        fi
        if [[ $(echo "${arr[@]: -1}") == "destroy" ]]; then
            if [ $i == "all" ]; then
                bash -c "$abs_path_folder_script/setup-swarm.sh destroy" || exit 1
                bash -c "$abs_path_folder_script/setup-monitoring.sh destroy" ||  exit 1
                bash -c "$abs_path_folder_script/setup-worker.sh ai down" || exit 1
                bash -c "$abs_path_folder_script/setup-metricserver.sh anomalies destroy" || exit 1
                bash -c "$abs_path_folder_script/setup-metricserver.sh autoscale destroy" || exit 1
            fi
            if [ $i == "swarm" ]; then
                bash -c "$abs_path_folder_script/setup-swarm.sh destroy"
            fi
            if [ $i == "worker" ]; then
                bash -c "$abs_path_folder_script/setup-worker.sh ai down"
            fi
            if [ $i == "monitoring" ]; then
                bash -c "$abs_path_folder_script/setup-monitoring.sh destroy"
            fi
            if [ $i == "anomalies" ]; then
                bash -c "$abs_path_folder_script/setup-metricserver.sh anomalies destroy"
            fi
            if [ $i == "autoscale" ]; then
                bash -c "$abs_path_folder_script/setup-metricserver.sh autoscale destroy"
            fi
            if [ $i == "cadvisor" ]; then
                bash -c "$abs_path_folder_script/setup-cadvisor.sh destroy"
            fi
            if [ $i == "node-exporter" ]; then
                bash -c "$abs_path_folder_script/setup-node-exporter.sh destroy"
            fi
            if [ $i == "visuallizer" ]; then
                bash -c "$abs_path_folder_script/setup-swarm-visuallizer.sh destroy -y"
            fi                
        fi
    done