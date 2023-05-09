from flask import Flask, request
import requests
import os
import json
import subprocess
from dotenv import load_dotenv

load_dotenv()
NAME_MANAGER=os.getenv('NAME_MANAGER')

app = Flask(__name__)                                                                                                                                                 

list_ip = []
worker_info = []
state = "stable"
targets = [{'target': 'cadvisor.json', 'port': "8080"}, # {'target': 'fluentd.json', 'port': "24224"}, 
           {'target': 'node-exporter.json', 'port': "9100"}]
path = '../../../Infrastructure/docker/conf/monitoring/prometheus/target/'

def detect_worker():
    global worker_info
    output1 = subprocess.Popen(['docker', 'node', 'ls'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output2 = subprocess.Popen(['grep', '-wv', str(NAME_MANAGER)], stdin=output1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, input = subprocess.Popen(['awk', '(NR>1){print $2}'], stdin= output2.stdout, stdout=subprocess.PIPE ,stderr=subprocess.PIPE).communicate()
    for name in output.decode('utf-8').split('\n'):
        if name != "":
            worker_sd = { "name" : str(name), "ip": ""}
            out1 = subprocess.Popen(['docker', 'node', 'inspect', str(name)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, inp = subprocess.Popen(['jq', '.[].Status.Addr'], stdin=out1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            IP = out.decode('utf-8').replace("\n", "").replace("\"", "")
            worker_sd["ip"] = str(IP)
            res = list(filter(lambda name_worker: name_worker["name"] == str(name), worker_info))
            if res != worker_sd:
                worker_info.append(worker_sd)
                update_worker_service(IP)
            else:
                continue
            
def update_worker_service(ip):
    for target in targets:
        targ = ip + ":" + target['port']
        with open(file=path+target['target'], mode='r+') as file:
            try:
                data = json.load(file)
                if targ not in data[0]['targets']:
                    data[0]['targets'].append(ip + ":" + target['port'])
                else:
                    print("Same !! Ignore it")
                file.seek(0)
                json.dump(data, file, indent=2)
            except json.decoder.JSONDecodeError:
                template = [
                            {
                                "labels": {
                                "job": target['target'].replace('.json', '')
                                },
                                "targets": [
                                ]
                            }
                            ]
                template[0]['targets'].append(ip + ":" + target['port'])
                file.seek(0)
                json.dump(template, file, indent=2)
                
def sd_nginx(list_ip):
    global state
    output1= subprocess.Popen(['docker', 'ps'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, int= subprocess.Popen(['grep', "-oE", "todo_server\.1\.[a-z0-9]+"], stdin=output1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    upstream = ""
    for ip in list_ip:
        if ip is list_ip[-1]:
            upstream += "    " + ip + ":3000 max_fails=2 fail_timeout=3;"
        else:
            upstream += "    " + ip + ":3000 max_fails=2 fail_timeout=3;" + "\n"
    try:
        if state == "scaling":
            template = r'''upstream todo_app {
    least_conn;
''' + upstream + r'''
}

server{
    listen 80 default_server;
    server_name _;
    location / {
        proxy_pass http://todo_app;
    }

    location /nginx_status {
        stub_status on;
        access_log off;
        allow 127.0.0.1;
        allow 172.21.0.0/16;
        deny all;
    }  
}'''
            conf_file = open("../../../Infrastructure/docker/conf/nginx/nginx-default.conf", "r+")
            conf_file.write(template)
            conf_file.close()
        else:
            os.system('cp -rf bak/nginx-default.conf.bak ../../../Infrastructure/docker/conf/nginx/nginx-default.conf')
        cmd_exec = "docker exec -it " + out.decode("utf-8").replace('\n','') + " service nginx reload > /dev/null"
        os.system(cmd_exec)
    except Exception as e:
        print("Error occurred while running -->" + str(e))
    
@app.route('/state_update', methods=['POST'])
def state_update():
    global state
    state = request.args.get('state')
    return "Ok"

@app.route('/join', methods=['POST'])
def join():
    detect_worker()
    return "Ok"
    

@app.route('/update', methods=['POST'])
def update():
    """
    Receive the infomation from slave and update into prometheus configuration
    """  
    ip = request.args.get('ip')
    hostname = request.args.get('hostname')
    update_worker_service(ip=ip)
    return "Ok"

@app.route('/sd', methods = ['POST'])
def sd():
    global list_ip, state
    temp_list_ip = request.json['sd_range']
    if list_ip == temp_list_ip:
        print("Not doing something")
        return "Ok"
    if list_ip != temp_list_ip:
        list_ip.clear()
        list_ip = temp_list_ip
        print("Doing something")
        sd_nginx(list_ip)
        return "Ok"

detect_worker()
# app.run(host='0.0.0.0', port='9999')