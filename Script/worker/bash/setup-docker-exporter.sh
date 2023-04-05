#!/bin/bash

if [[ "$1" == "create" ]]; then
    # create a daemon for purpose 
    sudo touch /etc/docker/daemon.json
    # Write the content for daemon.json to --> point metrics to 9323 port (Obligations Port Number)
    cat <<EOF | sudo tee -a /etc/docker/daemon.json > /dev/null
{
    "metrics-addr" : "0.0.0.0:9323"
}
EOF
    # Restart the service docker for update the new daemon.json
    sudo systemctl restart docker
    echo "Docker daemon is restarted successfully and can be accessed metrics via http://localhost:9323/metrics"
    exit 1
elif [[ "$1" == "destroy" ]]; then
    # Remove the daemon.json from /etc/docker/daemon.json for disconect the daemon to docker.sock
    sudo rm -rf /etc/docker/daemon.json
    # Restart the service docker for update the new config
    sudo systemctl restart docker
    echo "Docker daemon is destroyed successfully"
    exit 1
else
    echo "Unknown option: Choose one to start"
    exit 1
fi
