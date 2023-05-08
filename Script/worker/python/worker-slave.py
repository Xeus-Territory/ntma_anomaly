import requests
import socket
from dotenv import load_dotenv
import os
import subprocess
import time
import json

load_dotenv()
IP_MANAGER = os.getenv("IP_MANAGER")
OPENPORT = os.getenv("OPENPORT")

def info_host():
    """Pass the info of slave(ex: IP, Hostname, etc ...) to the worker manager

    Returns:
        string, string: Hostname, IP of slav
    """    
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        soc.connect(('8.8.8.8', 1))
        IP = soc.getsockname()[0]
    except:
        IP = socket.gethostbyname(socket.gethostname())
    
    return socket.gethostname(), IP

def info_service():
    """Service discovery for service web on slave
       # Solution: https://stackoverflow.com/questions/35086391/jq-how-to-iterate-through-keys-of-different-names
    
    Returns:
        The ip of service web app and applied into the worker manager
    """
    output1 = subprocess.Popen(["docker", "network", "inspect", "application"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, input = subprocess.Popen(["jq", "-jr", ".[].Containers[] | select(.Name != \"application-endpoint\") | .IPv4Address, \"\\t\""], 
                            stdin=output1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    list_ip = []
    for x in output.decode("utf-8").split("\t"):
        if x != "":
            list_ip.append(x.replace("/16",""))
    return list_ip
    

try:
    # hostname, ip = info_host()
    # params = {'hostname': hostname, 'ip': ip}
    # requests.post("http://" + IP_MANAGER + ":" + OPENPORT + "/update", params=params, headers={"Content-Type": "application/json"})
    while True:
        ip_list = {'sd_range': info_service()}
        requests.post("http://" + str(IP_MANAGER) + ":" + str(OPENPORT) + '/sd', data=json.dumps(ip_list), headers={"Content-Type": "application/json"})
        time.sleep(5)
except Exception as e: 
    print("Error occur: ", e)

