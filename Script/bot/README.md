# BOT FOR BENCHMARK AND INTERACTION WITH API

*This bot about alternative for easy using for benchmark and interact with API of webapp for ab. But the interact in about the template code for using for purpose --> Can be became the benchmark if you want to do what kind*

## Features
- Interact with API of web (Purpose for making a logs access and using that for apllied into AI data)
- Benchmarking performance API of webapp (Purpose for benchmarking performance, how much server can applied)

## Requirements:
- Make sure you have python3 and pip
- Install package about requirements.txt appears in Script directory

## Options for demend bot
### 1. Type of bot
>
> **-T or --type: purpose of type for doing with bot**
>
> valid options: -T interact, --type benchmark

### 2. Protocol
>
> **-P or --protocol: Protocol of request (HTTP or HTTPS). Default: HTTP**
>
> valid options: -P http, --protocol https

### 3. Location of URI
>
> **-l or --location_uri: URI for request with**
>
> valid options: -l localhost, --location_uri web.xyz

### 4. Port of URI want to request
>
> **-p or --port: Port of URI want to request. Default: 80**
>
> valid options: -p 80, --port 8080

### 5. Method of request (Can be one or multiple)
>
> **-m or --method: Method of request want to do**
>
> valid options: -m GET, --method GET POST PUT DELETE

### 6. Direction of request (Can be one or multiple /)
>
> **-d or --directory: Directory of request [More with interact but specify with benchmark]**
>
> valid options: -d /items, --directory / /items /menu

### 7. Timeout for bot working (Valid for both mode)
>
> **-t or --timeout: Timeout for bot working in (seconds). Default 30**
>
> valid options: -t 120, --timeout 0

### 8. Sleep for request (Valid for interact mode only)
>
> **-s or --sleep: Sleep for each request in (seconds). Default 5**
>
> valid options: -s 30, --sleep 5. Should be less than timeout but now it work if more (LOL that is bug)

### 9. Data template for Post requests (valid for interact mode only)
>
> **-D or --data_templates: Data template for post requests. Default {"name":"HelloWorld!!!"}. Work with dictionary type**
>
> valid options: -D {"name":"HelloWorld!!!"}, --data_templates {"name":"HelloWorld!!!", "message":"Welcome"}

### 10. Worker (Valid for benchmark mode only)
>
> **-w or --workers: Number of workers or concurence level for doing a job. Default 10**
>
> valid options: -w 10, --workers 100

### 11. Number_requests (Valid for benchmark mode only)
>
> **-n or --number_requests: Number of requests for benchmark mode. Default 100**
>
> valid options: -n 1000, --number_requests 1000000

## Common Example:
1. See the help for selected options

    `python3 demand_bot.py --help`

2. Common request for interaction mode

    `python3 demand_bot.py -T interactive -l localhost -d /items -m GET POST PUT DELETE -t 120 -s 30 -D {"name":"HelloWorld!!!"}`

3. Benchmarking

    `python3 demand_bot.py -T benchmark -l localhost -d /items -t 0 -w 100 -n 1000000`