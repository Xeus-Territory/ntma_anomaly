import csv
import re
from datatime import datatime

# str = r'10.0.0.2 - - [04/Apr/2023:07:11:48 +0000] "GET /js/react-dom.production.min.js HTTP/1.1" 304 0 "http://localhost/" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0" "-" "localhost" "_" "0.004"'

def generate_csv_log(filenames):
    log_pattern = re.compile(
    r'(?P<remote_addr>\d+\.\d+\.\d+\.\d+)\s' 
    r'(?P<remote_usr>\S+)\s'
    r'\S+\s'
    r'\[(?P<time_local>.*?)\]\s' 
    r'\"(?P<request_method>[A-Z]+)\s'
    r'(?P<request_url>[^"]+)\s'
    r'(?P<http_version>HTTP/\d\.\d)\"\s'
    r'(?P<status>\d+)\s'
    r'(?P<body_bytes_sent>\d+)\s'
    r'\"(?P<http_referer>[^"]+)\"\s'
    r'\"(?P<http_user_agent>[^"]+)\"\s'
    r'\"(?P<http_x_forwarded_for>[^"]+)\"\s'
    r'\"(?P<host>[^"]+)\"\s'
    r'\"(?P<server_name>[^"]+)\"\s'
    r'\"(?P<request_time>[^"]+)\"'
    )

    file = open(filenames, 'r')
    for line in file.readlines():
        log_filter = log_pattern.match(line)
        print(log_filter.groupdict()['time_local'])
    
generate_csv_log("/home/xeusnguyen/NTMA_Anomaly/Infrastructure/docker/log/access.log")