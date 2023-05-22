#!/bin/bash

### Update package in VM 
sudo apt update 
sudo apt upgrade -y

### Install docker
sudo apt install docker-compose -y

### Install az-cli
sudo apt install pass gnupg2 -y
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash