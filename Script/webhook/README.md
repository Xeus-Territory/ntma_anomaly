# Scaling Hook for doing control plane for swarm into scaling

*This module for doing a job scaling base on the metric of prometheus, currently. And AI for next few day*

## Features
- Control plane for scaling up and down for application in node
- Alert into API of telegram when scaling up executable

## Requirements:
- Make sure you have python3 and pip
- Install package about requirements.txt appears in Script directory

## Options for demend bot

### 1. Location of metric collection
>
> **-l or --location_uri: URI for request collection metric. More detail: Prometheus**
>
> valid options: -l http://localhost:9090/api/v1/alerts, --location_uri http://<IP_Prometheus>/api/v1/alerts

### 2. State of monitoring alert (Can be one or multiple)
>
> **-s or --state: State of monitoring alert for trigger scaling. Default: firing**
>
> valid options: -s firing, --state firing pending

### 3. Replica of application (Can be one or multiple)
>
> **-re or --replica: Max replica for scaling application. Default 1**
>
> valid options: -re 1, --replica 3

### 4. Metric of server (On Develop - Build Metric Server can serve for Prometheus)
>
> **-ms or --metric_server: Create HTTP server metric on specified port. Default: False**
>
> valid options: -ms False, --metric_server: True

### 5. Time to interval for scaling
>
> **-ti or --time_interval: Time interval to wait for replication scaling down --> [Untouchble Mode], in (seconds). Default 0**
>
> valid options: -ti 120, --time_interval 0

### 6. Time to metric
>
> **-tm or --time_metric: Time for update metric alert collect from Prometheus. Default 30**
>
> valid options: -tm 120, --time_metric 0

## Common Example:
1. See the help for selected options

    `python3 scaling_hook.py --help`

2. Common command can do fun running the scaling hook

    `python3 scaling_hook.py -l http://localhost:9090/api/v1/alerts -s firing pending -ti 30 -tm 0`