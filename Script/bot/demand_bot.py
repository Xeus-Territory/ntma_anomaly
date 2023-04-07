import json
import requests
import argparse
from sys import argv
import time
import random

def generate_random(type):
    if type == 'str':
        names=["We","I","They","He","She","Jack","Jim"]
        verbs=["was", "is", "are", "were"]
        nouns=["playing a game", "watching television", "talking", "dancing", "speaking"]
        return names[random.randint(0,len(names)-1)]+" "+verbs[random.randint(0,len(verbs)-1)]+" "+nouns[random.randint(0,len(nouns)-1)]
    if type == 'int':
        return random.randint(0, 100)     
    

def jobs_todo(work = "random", method = ['GET'] ,location_uri = "localhost", port = "80",  protocol = "http", url_point = [''] , data_in = {"name":"HelloWorld!!!"}, set_timeout=5.0):
    type_value_dict_key = [type(data_in[key]).__name__ for key in list(data_in.keys())]
    dict_key = list(data_in.keys())
    if work == "random":
        while set_timeout > 0:
            start_time = time.time()
            pick_one = random.choice(method)
            print(pick_one)
            pick_url = random.choice(url_point)
            if pick_one == "GET":
                requests.get(url=protocol + "://" + location_uri + ":" + port + pick_url)
            if pick_one == "POST":
                if pick_url == " ":
                    end_time = time.time()
                    set_timeout -= end_time - start_time
                    print(set_timeout)                    
                    continue
                else:
                    value_generate = [generate_random(x) for x in type_value_dict_key]
                    dict_generate = {dict_key[i]:value_generate[i] for i in range(len(dict_key))}
                    requests.post(url=protocol + "://" + location_uri + ":" + port + pick_url,
                                  headers={"Content-Type":"application/json"}, data=json.dumps(dict_generate))
            if pick_one == "PUT":
                if pick_url == " ":
                    end_time = time.time()
                    set_timeout -= end_time - start_time
                    print(set_timeout)
                    continue
                else:
                    response = requests.get(url=protocol + "://" + location_uri + ":" + port + pick_url)
                    if (len(response.json()) == 0) and (((len(method) <= 2 and (("DELETE" in method) or ("GET" in method))) or ((len(method) == 3 and (("DELETE" in method) and ("GET" in method)))))):
                        print("Not have anything, force stop to do anything")
                        set_timeout = 0
                        break
                    if len(response.json()) == 0:
                        end_time = time.time()
                        set_timeout -= end_time - start_time
                        print(set_timeout)
                        continue
                    if len(response.json()) > 1:
                        object_random = random.choice(response.json())
                        print(object_random)
                        if object_random['completed'] == False:
                            response = requests.put(url=protocol + "://" + location_uri + ":" + port + pick_url + "/" + object_random["id"], 
                                         headers={"Content-Type":"application/json"}, data='{\"name\":\"{0}\",\"completed\":true}'.format(object_random["name"]))
                        else:
                            response = requests.put(url=protocol + "://" + location_uri + ":" + port + pick_url + "/" + object_random["id"], 
                                         headers={"Content-Type":"application/json"}, data='{"name":"{0}","completed":false}'.format(object_random["name"]))                            
                        print(response.status_code)
            end_time = time.time()
            set_timeout -= end_time - start_time
            print(set_timeout)
            
jobs_todo(method= ['PUT'], url_point=['/items'], set_timeout=0.05)

# TYPE = ['demand', 'dos']

# parser = argparse.ArgumentParser(description="Bot for request to web with purpose")
# parser.add_argument('-ty', '--type', help='purpose of type for doing with bot', choices=TYPE, required=True)
# parser.add_argument('-t' , '--timer', help='timer give for bot in (seconds)', required=True)
# parser.add_argument('-m' , '--method', help='method of request', nargs='+', required=TYPE[0] in argv)
# opt = parser.parse_args()

# type_choice = opt.type
# set_time = float(opt.timer)
# if opt.type == "demand":
#     while set_time > 0:
#         start_time = time.time()
#         get_todo()
#         job_done = time.time()
#         set_time -= job_done - start_time
#         print(set_time)