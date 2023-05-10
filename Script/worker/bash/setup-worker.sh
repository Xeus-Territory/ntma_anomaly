#!/bin/bash

abs_path_file_execute=$(realpath "$0")
abs_path_folder_root=$(dirname "$(dirname "$(dirname "$(dirname "$abs_path_file_execute")")")")

if [ $1 == "up" ]; then
    docker stack deploy -c "$abs_path_folder_root/bww-compose.yaml" worker || exit 1
elif [ $1 == "down" ]; then
    docker stack rm worker || exit 1
else
    echo "Error: Unknown the optional for this script"
fi