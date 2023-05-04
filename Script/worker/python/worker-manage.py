from flask import Flask, request
import requests
import os
import json
import subprocess

app = Flask(__name__)                                                                                                                                                 

list_ip = []
state = "stable"
targets = [{'target': 'cadvisor.json', 'port': "8080"}, {'target': 'fluentd.json', 'port': "24224"}, {'target': 'node-exporter.json', 'port': "9100"}]
path = '../../../Infrastructure/docker/conf/monitoring/prometheus/target/'

def update_target(ip):
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
    

@app.route('/update', methods=['POST'])
def update():
    """
    Receive the infomation from slave and update into prometheus configuration
    """  
    ip = request.args.get('ip')
    hostname = request.args.get('hostname')
    update_target(ip=ip)
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

app.run(host='0.0.0.0', port='9999')