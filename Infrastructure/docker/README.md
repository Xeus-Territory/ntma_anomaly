# Docker V0.1.0

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
>
> Listing Kafka topics: `kafka-topics.sh --list --zookeeper zookeeper:2181`
>
> Kafka console Producers: `kafka-console-producer.sh --broker-list kafka:9092 --topic topic_name`
> 
> Kafka console Consumers: `kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic topic_name`

# Docker V0.2.0
![Update](https://media2.giphy.com/media/2x0tJVAL3IqFnZYhYt/giphy.gif)
## New Features and New Components
1. New Components
- log_data: Folder will be created by deployment anomalies metric detection block. It will storage log by hours for each file log. (That part can be used for AI-DL model)
- metrics-csv: Container convert metrics from Redis captures by kafka to CSV format. Contents in log_data is resulted by this one.
- metrics-redis: Container captures metrics from kafka-prometheus producer and store them in redis by kafka-comsumer
- dockerfile.nginx (Complicated part): That will completely install many conponent inside dockefile related by compile LuaJIT, RestyCore, Modsecurity, ...
- yaml: file for orchestration using docker-swarm and docker-compose (all in one)

2. New Features
- Captured Message inside the kafka and export log into file in hour and existed in CSV format (Optimze log for for searching and analysis than huge log file)
- Have Passive and Active firewall
    - Passive firewall created and using for block DDoS, DoS and Request by port scan. Compile and write in LUA script and intergrate inside NGINX server
    - Active firewall created and using for web attack with OWASP rules like SQL injection, XSS, XXE, .... Compile and intergrate in NGINX with mod-security writed by C

## New way to stored image
- Anything image on that repository will be stored on DockerHub and that have way to build that by using the [script-file](../../docker-build-image.sh)

## New way to run the components in one command
- That thing created inside the script file if you want to deploy [AI](../../setup-all-ai.sh) or [Metrics](../../setup-all-metric.sh)