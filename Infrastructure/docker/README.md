# Docker

*Contain anything of system inside docker*

## Requirements
*All thing in that folder should be setup in env Docker so need to install docker first*
>
> Installing docker into Linux (Ubuntu, Debian, ...)
>
> Run:  `sudo apt update && sudo apt install docker-compose -y`
>
> Run:  `sudo usermod -aG docker <username of distro>`
>
> Installing docker into Windows
>
> Go to https://docs.docker.com/desktop/install/windows-install/ for more information

## Content of:
- app: include anything about source code of website to deploy into docker
- conf: include any configuration about the Prometheus, Grafana dashboard, nginx, nginx-log, zookeeper, etc
- log: contain log from nginx to logging when nginx running, using backup and applied for another module on system
- dockerfile.*: file for building image base on specified target. Example: dockerfile.nginx for building compile modsecurity into nginx and make module work in side container nginx.
- *.yaml: file for build and run image using docker-compose to deploy into docker

## Features:
- Using docker swarm (like k8s but not have advanced features like autoscaling base control plan like one) for orchestrating system configuration
- Applied SD for dynamic update system configuration and make anything became automatically
- Using Grafana env for visualization and prometheus to monitoring the metrics on system
- All in one for doing the message queues for convert metric into message and store into redis via kafka and kafka stream for use data into next step about model AI
- Preventing the webattack threading from modsecurity installed into NGINX

## Port will be opened to access into: 
- 80  : Application
- 3000: Grafana
- 9090: Prometheus
- 8081: docker-swarm-visualizer
- 9999: Api for monitoring to orchestrating system configuration in node manager

## Interactive with redis
> **NOTE**
>
> Run: `docker compose -f get-data-metric-compose.yaml up -d`
>
> wait a few seconds after the kafka service is up
>
> Run: `docker exec -it redis redis-cli`
>
> Command: `KEYS *` => Review.