from flask import Flask, request
import requests
import os
import json

app = Flask(__name__)                                                                                                                                                 

list_ip = []
targets = [{'target': 'cadvisor.json', 'port': "8080"}, {'target': 'fluentd.json', 'port': "24224"}, {'target': 'node-exporter.json', 'port': "9100"}]
path = '../../../Infrastructure/docker/conf/monitoring/prometheus/target/'

def update_target(ip):
    for target in targets:
        with open(file=path+target['target'], mode='r+') as file:
            try:
                data = json.load(file)
                data[0]['targets'].append(ip + ":" + target['port'])
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
    global list_ip
    # temp_list_ip = request.json
    print(request.json['sd_range'])
    return "Ok"


app.run(host='0.0.0.0', port='9999')