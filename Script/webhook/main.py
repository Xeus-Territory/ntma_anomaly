from flask import Flask, request
from dotenv import load_dotenv
import os
import telebot
import threading
import requests
import time

# Get environment variable 
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID   = os.getenv('CHAT_ID')

bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

# Basic parameters of prometheus and infra settings
replica_name = []
monitoring_alert_prometheus = []
current_replica = 1
thread_list = []
scale_down_flag = False

def send_test_message(data):
    """Generates a Message object and sends it to the telegram by bot

    Args:
        data (dict): data get from the resquest json
    """    
    try:
        # print(data)
        message = "=========🔥 Alert 🔥========= " \
        + "\nStatus: "          + data["status"] \
        + "\n\nLabels:" \
        + "\n  → Alertname: "   + data["labels"]["alertname"] \
        + "\n  → Instance: "    + data["labels"]["instance"] \
        + "\n  → Severity: "    + data["labels"]["severity"] \
        + "\n\nAnnotations:" \
        + "\n  → Description: " + data["annotations"]["description"] \
        + "\n  → Summary: "     + data["annotations"]["summary"] \
        + "\n\nStarts at: "     + data["startsAt"] \
        + "\nEnds at: "         + data["endsAt"] \
        + "\n================= \n"

        bot.send_message(CHAT_ID, message)
    except Exception as ex:
        print(ex)
        
def check_health_alert(deplay_check_time=30):
    global monitoring_alert_prometheus
    while True:
        response = requests.get('http://localhost:9090/api/v1/alerts')
        monitoring_alert = response.json()['data']['alerts']
        if len(monitoring_alert) == 0:
            monitoring_alert_prometheus = []
            time.sleep(deplay_check_time)
        if len(monitoring_alert) > 0:
            for index in range(0, len(monitoring_alert)):
                if monitoring_alert[index]['labels']['name'] not in monitoring_alert_prometheus:
                    monitoring_alert_prometheus.clear()
                    monitoring_alert_prometheus.append(monitoring_alert[index]['labels']['name'])
            time.sleep(deplay_check_time)
            
            
        
def scaling_replica(name_container, max_scaling_service=1):
    """Scaling job for a given

    Args:
        name_service (string): which container of service meet trouble and need to scale
        max_scaling_service (int): maximum scaling service can be reached for this container. Default = 1

    """
    global monitoring_alert_prometheus, replica_name, current_replica, scale_down_flag
    print("Scaling up for dedicated " + name_container + " .....")
    os.system('./scale-service-swarm.sh ' + name_container + ' ' + "up " + str(max_scaling_service))
    print("Scaling successful for " + name_container)
    current_replica += max_scaling_service
    while True:
        if name_container in monitoring_alert_prometheus:
            continue
        if name_container not in monitoring_alert_prometheus:
            if scale_down_flag == False:
                scale_down_flag = True
                os.system('./scale-service-swarm.sh ' + name_container + ' ' + "down " + str(max_scaling_service))
                current_replica -= max_scaling_service
                replica_name.remove(name_container)
                print("The current replica is scaling down, application have stable state !!!!")
                scale_down_flag = False
                break
            if scale_down_flag == True:
                continue

    
def scaling_node(name_node, max_scaling_node=1):
    pass
    
# @app.route('/alerts', methods=['POST'])
# def alerts():
#     """Receive alerts from prometheus and trigger scale and notify for telegram

#     Returns:
#         string: "OK" for comfirm everything is work
#     """
#     data = request.json
#     # Your analysis and processing here!
#     for index in range(0, len(data["alerts"])):
#         if data['alerts'][index]['labels']['name'] not in replica_name:
#             replica_name.append(data['alerts'][index]['labels']['name'])
#             threading.Thread(target=scaling_replica, args=(data['alerts'][index]['labels']['name'], 1)).start()

#     # Send alert to telegram
#     # send_test_message(data)
#     return 'OK'

# Run a webhook for listening the alert and trigger scaling
# app.run(host="0.0.0.0", port="5000")

# Start thread for checking health of prometheus 
threading.Thread(target=check_health_alert).start()

while True: 
    try:
        print("Result Replica: ", replica_name)
        print("Result Alert Pull: ", monitoring_alert_prometheus)
        print("Result ReplicaNumber:", current_replica)
        print(scale_down_flag)
        time.sleep(3)
        response = requests.get('http://localhost:9090/api/v1/alerts')
        alerts = response.json()['data']['alerts']
        for index in range(0, len(alerts)):
            if alerts[index]['labels']['name'] not in replica_name:
                replica_name.append(alerts[index]['labels']['name'])
                threading.Thread(target=scaling_replica, args=(alerts[index]['labels']['name'], 1)).start()
    except KeyboardInterrupt:
        exit(1)
