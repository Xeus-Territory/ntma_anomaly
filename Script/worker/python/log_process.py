import csv
import re
import os
from datetime import datetime
from sys import argv

def check_pattern_log_datetime(log_file_path):
    """ Checks the pattern of log a return timestamp and valid log

    Args:
        log_file_path (string): path to the log file

    Returns:
        (list, list): Return twice list of strings, first for log and second for timestamp
    """
    date_arr = []
    log_arr = []
    file = open(log_file_path, 'r')
    reg_log_pattern = re.compile(
        r'(?P<remote_addr>\d+\.\d+\.\d+\.\d+)\s'        # Check remote_addr like 10.0.0.2
        r'(?P<remote_usr>\S+)\s'                        # Check remote_usr like - -, Get the string inside and if it empty return ""
        r'\S+\s'                                        # Remove the space before the time_local
        r'\[(?P<time_local>.*?)\]\s'                    # Check time_local like [04/Apr/2023:07:11:48 +0000], return string inside the brackets
        r'\"(?P<request_method>[A-Z]+)\s'               # Check request method like GET, POST, PUT, DELETE
        r'(?P<request_url>[^"]+)\s'                     # Check request uri like /js/react-dom.production.min.js
        r'(?P<http_version>HTTP\/\d\.\d)\"\s'            # Check http version like HTTP/1.1
        r'\"(?P<request_body>.*?)\"\s'                  # Check request body
        r'(?P<status>\d+)\s'                            # Check the status respone 304, 200, ...
        r'(?P<body_bytes_sent>\d+)\s'                   # Get the number byte send, for purpose like 0, 255
        r'\"(?P<http_referer>[^"]+)\"\s'                # Get the http reference like http://localhost/
        r'\"(?P<upstream_addr>[^"]+)\"\s'               # Get the upstream address 
        r'(?P<upstream_status>\d+)\s'                   # Get the upstream status
        r'\"(?P<http_user_agent>[^"]+)\"\s'             # Get the http user agent like Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0
        r'\"(?P<http_x_forwarded_for>[^"]+)\"\s'        # Get the http x_forwarded_for like ip, ...
        r'\"(?P<host>[^"]+)\"\s'                        # Get the host for the server like localhost
        r'\"(?P<server_name>[^"]+)\"\s'                 # Get and check server name like _ if null, or something else
        r'\"(?P<request_time>[^"]+)\"\s'                # Get request time 
        r'\"(?P<upstream_response_time>[^"]+)\"\s'      # Get response upstream time
        r'\"(?P<upstream_connection_time>[^"]+)\"\s'    # Get upstream connection time
    )
    for line in file.readlines():
        if reg_log_pattern.match(line) is not None:
            temp = datetime.strptime(reg_log_pattern.match(line).groupdict()['time_local'], "%d/%b/%Y:%H:%M:%S %z").date()
            if (str(temp) not in date_arr):
                date_arr.append(str(temp))
            log_arr.append(reg_log_pattern.match(line).groups())

    file.close()
    truncate_file = open(log_file_path, 'w')
    truncate_file.truncate()
    truncate_file.close
    
    return log_arr, date_arr


def create_folder_by_datetime(date_arr):
    """Create a folder by datetime

    Args:
        date_arr (list): list of datetime

    Returns:
        list: list of strings representing for folder storage log
    """    
    path_folder_create = []
    for date in date_arr:
        path = "../../../Infrastructure/docker/log/" + date
        if not os.path.exists(path):
            os.makedirs(path)
            path_folder_create.append(path)
        elif path not in path_folder_create:
            path_folder_create.append(path)
        else:
            continue
    return path_folder_create
            

def generate_csv_log(log_file_path, namefile="raw_data.csv"):
    """Generate a new csv file for each log file when function access

    Args:
        log_file_path (string): path of log file
        namefile (str, optional): name of file csv will generate. Defaults to "raw_data.csv".
    """    
    log_arr, date_arr = check_pattern_log_datetime(log_file_path)
    folder_store_csv = create_folder_by_datetime(date_arr)
    for folder_store in folder_store_csv:
        if not os.path.exists(folder_store + "/" +namefile):
            output = open(folder_store + "/" +namefile, 'w')
            csv_out = csv.writer(output)
            csv_out.writerow(['remote_addr', 'remote_usr', 'time_local', 'request_method', 'request_url',
                            'http_version', 'request_body', 'status', 'body_bytes_sent', 'http_referer', 'upstream_addr',
                            'upstream_status', 'http_user_agent', 'http_x_forwarded_for', 'host', 'server_name', 'request_time',
                            'upstream_response_time', 'upstream_connection_time'])
        else:
            output = open(folder_store + "/" +namefile, 'a')
            csv_out = csv.writer(output)

        for log in log_arr:
            if str(datetime.strptime(log[2], "%d/%b/%Y:%H:%M:%S %z").date()) in folder_store:
                temp = list(log)
                temp[6] = str(log[6]).encode('utf-8').decode('unicode_escape')
                log = tuple(temp)
                csv_out.writerow(log)
            else:
                continue
        output.close()
    
def __main__():
    try:
        if argv[1] != "":
            try:
                generate_csv_log(argv[1])
            except FileNotFoundError:
                print("Something wrong on your file, It doesn't exist or wrong path. Try Again !!!")
                return
    except IndexError:
        print("Missing a path for the log file, pass in and try again !!!")
        return
        
if __name__ == '__main__':
    __main__()