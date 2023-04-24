import requests
import socket
from dotenv import load_dotenv
import os

load_dotenv()
IP_MANAGER = os.getenv("IP_MANAGER")
OPENPORT = os.getenv("OPENPORT")

def info_host():
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        soc.connect(('8.8.8.8', 1))
        IP = soc.getsockname()[0]
    except:
        IP = socket.gethostbyname(socket.gethostname())
    
    return socket.gethostname(), IP

try:
    hostname, ip = info_host()
    params = {'hostname': hostname, 'ip': ip}
    requests.post("http://" + IP_MANAGER + ":" + OPENPORT + "/update", params=params, headers={"Content-Type": "application/json"})
except Exception as e: 
    print("Error occur: ", e)

