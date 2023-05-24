#!/bin/bash

### Update package in VM 
sudo apt update 
sudo apt upgrade -y

### Install docker
sudo apt install docker-compose -y

### Install az-cli
sudo apt install pass gnupg2 -y
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

### Install and enable Cadvisor
curl -L https://github.com/google/cadvisor/releases/download/v0.47.0/cadvisor-v0.47.0-linux-amd64 -o cadvisor
chmod +x cadvisor | sudo mv cadvisor /usr/local/bin
cat << EOF | sudo tee /etc/systemd/system/cadvisor.service > /dev/null
[Unit]
Description=Cadvisor
Documentation=https://github.com/google/cadvisor
After=network-online.target

[Service]
User=root
ExecStart=/usr/local/bin/cadvisor  $OPTIONS
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl enable cadvisor.service

### Install and enable node-exporter
curl -LO https://github.com/prometheus/node_exporter/releases/download/v1.5.0/node_exporter-1.5.0.linux-amd64.tar.gz
tar -xvf node_exporter-1.5.0.linux-amd64.tar.gz > /dev/null
sudo mv node_exporter-1.5.0.linux-amd64/node_exporter /usr/local/bin
rm -rf node_exporter-1.5.0.linux-amd64.tar.gz && rm -rf node_exporter-1.5.0.linux-amd64
# Write the service for systemd and start it --> The node exporter will run on port 9100
cat << EOF | sudo tee /etc/systemd/system/node_exporter.service > /dev/null
[Unit]
Description=Prometheus Node Exporter
Documentation=https://github.com/prometheus/node_exporter
After=network-online.target

[Service]
User=root
ExecStart=/usr/local/bin/node_exporter  $OPTIONS
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl enable node_exporter.service