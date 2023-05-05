from flask import Flask, request
from dotenv import load_dotenv
import os
import telebot
import threading
import requests
import time
import argparse
import math
import subprocess

# Get environment variable 
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID   = os.getenv('CHAT_ID')

bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

# Basic parameters of prometheus and infra settings
replica_name = []
monitoring_alert_prometheus = []
total_replica = 1
active_replica = 1
scale_down_flag = False
state_hook = "stable"
state_compare = "stable"

def send_test_message(data):
    """Generates a Message object and sends it to the telegram by bot

    Args:
        data (dict): data get from the resquest json
    """    
    try:
        message = "=========🔥 Alert 🔥========= " \
        + "\n\nLabels:" \
        + "\n  → Alertname: "   + str(data["labels"]["alertname"]) \
        + "\n  → Instance: "    + str(data["labels"]["instance"]) \
        + "\n  → Severity: "    + str(data["labels"]["severity"]) \
        + "\n\nAnnotations:" \
        + "\n  → Description: " + str(data["annotations"]["description"]) \
        + "\n  → Summary: "     + str(data["annotations"]["summary"]) \
        + "\n\nStarts at: "     + str(data["activeAt"]) \
        
        bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as ex:
        print("Error occured with err: ", ex)
        
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
    
def check_health_alert(url_metric, state_health_check, deplay_check_time=30):
    """Check health from status return Metrics collection. Example Prometheus (Not template: Just custom for Prometheus)

    Args:
        deplay_check_time (int, optional): Time for check the alert status. State Pulling. Defaults to 30.
    """
    
    global monitoring_alert_prometheus, total_replica, active_replica, state_hook
    while True:
        response = requests.get(url_metric)
        monitoring_alert = response.json()['data']['alerts']
        active_replica, total_replica = enum_replica()
        if len(monitoring_alert) == 0:
            monitoring_alert_prometheus = []
            state_hook = "stable"
            time.sleep(deplay_check_time)
        if len(monitoring_alert) > 0:
            monitoring_alert_prometheus.clear()
            state_hook = "scaling"
            for index in range(0, len(monitoring_alert)):
                if (monitoring_alert[index]['labels']['name'] not in monitoring_alert_prometheus) and (monitoring_alert[index]['state'] in state_health_check):
                    monitoring_alert_prometheus.append(monitoring_alert[index]['labels']['name'])
            time.sleep(deplay_check_time)
            
            
        
def scaling_replica(name_container, time_untouchable, max_scaling_service=1):
    """Scaling job for a given

    Args:
        name_service (string): which container of service meet trouble and need to scale
        max_scaling_service (int): maximum scaling service can be reached for this container. Default = 1

    """
    global monitoring_alert_prometheus, replica_name, current_replica, scale_down_flag
    # print("Scaling up for dedicated " + name_container + " .....")
    os.system('./scale-service-swarm.sh ' + name_container + ' ' + "up " + str(max_scaling_service))
    # print("Scaling successful for " + name_container)
    while True:
        if time_untouchable == math.inf:
            continue
        else:
            time.sleep(time_untouchable)
            time_untouchable = 0
            if name_container in monitoring_alert_prometheus:
                continue
            if name_container not in monitoring_alert_prometheus:
                if scale_down_flag == False:
                    scale_down_flag = True
                    os.system('./scale-service-swarm.sh ' + name_container + ' ' + "down " + str(max_scaling_service))
                    replica_name.remove(name_container)
                    # print("The current replica is scaling down, application have stable state !!!!")
                    scale_down_flag = False
                    break
                if scale_down_flag == True:
                    continue

    
def scaling_node(max_scaling_node=1):
    pass


def __main__():
    """Argparse function for doing the customization of scaling
    """    
    parser = argparse.ArgumentParser(description="Scaling Hook with Metrics and Alerts")
    parser.add_argument("-l", "--location", help="Metric collection location. Ex: http://<IP_Prometheus>/api/v1/alerts", default='http://localhost:9090/api/v1/alerts')
    parser.add_argument("-s", "--state", help="State of monitoring alert", nargs="+", default=['firing'])
    parser.add_argument("-re", "--replica", help="Max replica for scaling application", type=int, default=1)
    parser.add_argument("-ms", "--metric_server", help="Create HTTP server metric on specified port", type=bool, default=False)
    parser.add_argument("-ti", "--time_interval", help="Time interval to wait for replication scaling down --> [Untouchble Mode], in seconds", type=float, default=0)
    parser.add_argument("-tm", "--time_metric", help="Time for update metric alert collect from Prometheus", type=int, default=30)
    opt  = parser.parse_args()
    
    location_prometheus = opt.location
    state_alert = opt.state
    max_replica = opt.replica
    metric_server_state= opt.metric_server
    time_interval = opt.time_interval   
    time_metric = opt.time_metric
    
    # Start thread for checking health of prometheus 
    threading.Thread(target=check_health_alert, args=(location_prometheus, state_alert, time_metric)).start()

    # Start While loop for doing the job scaling base on alert pulling
    while True: 
        try:
            global state_hook, state_compare
            if state_hook != state_compare:
                try:
                    requests.post("http://worker_manager:9999/state_update", params={'state': state_hook}, headers={'Content-Type': 'application/json'})
                except:
                    requests.post("http://localhost:9999/state_update", params={'state': state_hook}, headers={'Content-Type': 'application/json'})
                state_compare = state_hook
            # print("Number of replicas [active/total]: {active}/{total}".format(active=active_replica, total=total_replica))
            # print("Alert Pulling: " , monitoring_alert_prometheus)
            # print("Scaling Alert: " , replica_name)
            # print("Flag scaling down: ", scale_down_flag)
            # time.sleep(3)
            # The URL of Prometheus not Templated
            response = requests.get(location_prometheus)
            alerts = response.json()['data']['alerts']
            print(len(alerts))
            if (len(alerts) > 0):
                for index in range(0, len(alerts)):
                    try:
                        if (alerts[index]['labels']['name'] not in replica_name) and (alerts[index]['state'] in state_alert):
                            replica_name.append(alerts[index]['labels']['name'])
                            threading.Thread(target=scaling_replica, args=(alerts[index]['labels']['name'], time_interval, max_replica)).start()
                            send_test_message(alerts[index])
                    except:
                        scaling_node()
                        send_test_message(alerts[index])
            else:
                continue
        except:
            exit(0)
            
if __name__ == '__main__':
    __main__()
