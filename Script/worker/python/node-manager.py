from flask import Flask, request
import requests
import os
import json
import subprocess
from dotenv import load_dotenv
import time
import threading
import telebot

load_dotenv()
NAME_MANAGER=os.getenv('NAME_MANAGER')
IP_MANAGER=str(os.getenv('IP_MANAGER'))
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID   = os.getenv('CHAT_ID')
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)                                                                                                                                                 

list_ip = []
worker_info = []
state = "stable"
targets_worker = [{'target': 'cadvisor.json', 'port': "8080"}, # {'target': 'fluentd.json', 'port': "24224"}, 
           {'target': 'node-exporter.json', 'port': "9100"}]
targets_manager = [{'target': 'nginx-exporter.json', 'port': "9113"}, {'target': 'nginxlog-exporter.json', 'port': "4040"}]          
path = '../../../Infrastructure/docker/conf/monitoring/prometheus/target/'

def detect_worker():
    """
        Detects a worker join into a docker swarm cluster
    """    
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
                update_service(ip=IP, targets=targets_worker)
            else:
                continue
            
def update_service(ip, targets):
    """Update the worker service for the prometheus target

    Args:
        ip (str): The ip address of the worker node join into docker swarm cluster
    """    
    if ip == "":
        return
    for target in targets:
        targ = ip + ":" + target['port']
        with open(file=path+target['target'], mode='r+') as file:
            try:
                data = json.load(file)
                if targ not in data[0]['targets']:
                    data[0]['targets'].append(targ)
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
                template[0]['targets'].append(targ)
                file.seek(0)
                json.dump(template, file, indent=2)

def nginx_update(sleep_time):
    output1= subprocess.Popen(['docker', 'ps'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, int= subprocess.Popen(['grep', "-oE", "todo_server\.1\.[a-z0-9]+"], stdin=output1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    time.sleep(sleep_time)
    cmd_exec = "docker exec " + out.decode("utf-8").replace('\n','') + " service nginx reload > /dev/null"
    os.system(cmd_exec)
                
def sd_nginx(list_ip):
    """The module for managing the confi of nginx for change round-robin to lease connection and reverse

    Args:
        list_ip (list[str]): list of IP addresses of container have running the application 
        for put into upstream inside nginx container
    """    
    global state
    upstream = ""
    for ip in list_ip:
        if ip is list_ip[-1]:
            upstream += "    " + "server " + ip + ":3000 max_fails=2 fail_timeout=3;"
        else:
            upstream += "    " + "server " + ip + ":3000 max_fails=2 fail_timeout=3;" + "\n"
    try:
        if state == "scaling":
            template = r'''upstream todo_app {
    least_conn;
''' + upstream + r'''
}

server{
    listen 80 default_server;
    server_name _;
    modsecurity on;
    modsecurity_rules_file /etc/nginx/modsec/main.conf;

    location ~ "\/items\/([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})" {
        modsecurity off;
        proxy_pass http://todo_app;
    }
    
    location / {
        proxy_pass http://todo_app;
    }

    location /nginx_status {
        access_by_lua_block {return}
        stub_status on;
        access_log off;
        allow 127.0.0.1;
        allow 172.21.0.0/16;
        deny all;
    }  
}

include /etc/nginx/waf/ddos.conf;'''
            conf_file = open("../../../Infrastructure/docker/conf/nginx/nginx-default.conf", "r+")
            conf_file.truncate()
            conf_file.write(template)
            conf_file.close()
            threading.Thread(target=nginx_update, args=[30]).start()
        else:
            os.system('cp -rf bak/nginx-default.conf.bak ../../../Infrastructure/docker/conf/nginx/nginx-default.conf')
            threading.Thread(target=nginx_update, args=[3]).start()

    except Exception as e:
        print("Error occurred while running -->" + str(e))

def enum_replica():
    """
    Replica information of application on swarm

    Returns:
        _type_: _description_
    """    
    output = subprocess.Popen(['docker', 'service', 'ls'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output1 = subprocess.Popen(['grep', 'app'], stdin=output.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, inp=  subprocess.Popen(['awk', '{print $4}'], stdin=output1.stdout, stdout=subprocess.PIPE).communicate()
    return out.decode('utf-8').replace('\n', '').split('/')[0], out.decode('utf-8').replace('\n', '').split('/')[1]
        
def scaling_app(state, replica, message):
    """Scaling todo_app in docker swarm via request come from manager worker

    Args:
        state (string): state of scaling request. Choice one of ['up' or 'down']
        replica (string): number of replica want to update after scaling up or down
    """    
    active_replica, total_replica = enum_replica()
    if state == "up":
        bot.send_message(chat_id=CHAT_ID, text=message)
        os.system("docker service scale todo_app="+ str(int(active_replica) + int(replica)))
    if state == "down":
        if int(active_replica) == 1:
            pass
        if int(active_replica) > 1:
            if (int(active_replica) - int(replica)) >= 1:
                bot.send_message(chat_id=CHAT_ID, text=message)
                os.system("docker service scale todo_app=" + str(int(active_replica) - int(replica)))
            else:
                pass
            
def firewall_interact(state):
    if state == "up":
        os.system("cp -rf bak/ddos-default.conf.bak ../../../Infrastructure/docker/conf/nginx/ddos.conf")
        bot.send_message(chat_id=CHAT_ID, text="Passive Firewall is turning on")
    if state == "down":
        with open("../../../Infrastructure/docker/conf/nginx/ddos.conf", 'r+') as f:
            f.truncate()
            f.close()
        bot.send_message(chat_id=CHAT_ID, text="Passive Firewall is turning off")
    output1= subprocess.Popen(['docker', 'ps'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, int= subprocess.Popen(['grep', "-oE", "todo_server\.1\.[a-z0-9]+"], stdin=output1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    cmd_exec = "docker exec " + out.decode("utf-8").replace('\n','') + " service nginx reload > /dev/null"
    os.system(cmd_exec)

            
@app.route('/state_update', methods=['POST'])
def state_update():
    """Update the state of system on state scaling or stable for doing a job with that flag

    Returns:
        str: just return the str for resprsent for this route
    """    
    global state
    state = request.args.get('state')
    return "Ok"

@app.route('/join', methods=['POST'])
def join():
    """Update the worker join into the swarm cluster on role worker node

    Returns:
        str: just return the str for resprsent for this route
    """    
    detect_worker()
    return "Ok"
    

@app.route('/update', methods=['POST'])
def update():
    """Receive the infomation from slave and update into prometheus configuration
    
    Returns:
        str: just return the str for resprsent for this route
    """  
    ip = request.args.get('ip')
    hostname = request.args.get('hostname')
    update_service(ip=ip, targets=targets_worker)
    return "Ok"

@app.route('/sd', methods = ['POST'])
def sd():
    """Receive the request for service discovery for update the nginx service 
    
    Returns:
        str: just return the str for resprsent for this route
    """  
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

@app.route('/scaling', methods= ['POST'])
def scaling():
    replica = request.args.get('replica')
    state = request.args.get('state')
    message = request.args.get('message')
    scaling_app(state=state, replica=replica, message=message)
    return "Ok"

@app.route('/firewall', methods= ['POST'])
def firewall():
    state = request.args.get('state')
    firewall_interact(state=state)
    return "Ok"

@app.route('/security_info', methods= ['POST'])
def security_info():
    density = request.args.get('density')
    bot.send_message(chat_id=CHAT_ID, text="Current Density of Normals/Totals: {density}".format(density=density))
    return "Ok"

def __main__():
    update_service(ip=IP_MANAGER, targets=targets_manager)

    app.run(host='0.0.0.0', port='9999')
    
if __name__ == '__main__':
    __main__()