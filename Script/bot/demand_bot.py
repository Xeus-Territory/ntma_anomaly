import json
import requests
import argparse
from sys import argv
import time

def get_todo():
    requests.get('http://localhost/items')
    
TYPE = ['demand', 'dos']

parser = argparse.ArgumentParser(description="Bot for request to web with purpose")
parser.add_argument('-ty', '--type', help='purpose of type for doing with bot', choices=TYPE, required=True)
parser.add_argument('-t' , '--timer', help='timer give for bot in (seconds)', required=True)
parser.add_argument('-m' , '--method', help='method of request', nargs='+', required=TYPE[0] in argv)
opt = parser.parse_args()

type_choice = opt.type
set_time = float(opt.timer)
if opt.type == "demand":
    while set_time > 0:
        start_time = time.time()
        get_todo()
        job_done = time.time()
        set_time -= job_done - start_time
        print(set_time)