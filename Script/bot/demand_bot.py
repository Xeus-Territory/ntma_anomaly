import json
import requests
import argparse
from sys import argv, path
import time
import random
import os
import datetime


def generate_random_todo(type):
    """
    Generates a random number or string
    
    Args:
        type (str): type to pick generate

    Returns:
        str or int: return the generated sentence for todo
    """ 
    if type == 'str':
        names=["We","I","They","He","She","Jack","Jim"]
        verbs=["was", "is", "are", "were"]
        nouns=["playing a game", "watching television", "talking", "dancing", "speaking"]
        return names[random.randint(0,len(names)-1)]+" "+verbs[random.randint(0,len(verbs)-1)]+" "+nouns[random.randint(0,len(nouns)-1)]
    if type == 'int':
        return random.randint(0, 100)     
    

def interact_todo(method = ['GET'] ,location_uri = "localhost", port = "80",  protocol = "http", dir_point = ['/'] ,
                  data_template = {"name":"HelloWorld!!!"}, set_timeout=5.0, sleep_timeout=2):
    """
    Make a request to do something to generate logging with interacting via REST API.
    
    Args:
        method (list, optional): Method to interact with API. Defaults to ['GET'] and can be ['POST', 'PUT,' or 'DELETE']
        location_uri (str, optional): The URI for Bot interact with API. Defaults to "localhost".
        port (str, optional): Port URI to interact with. Defaults to "80".
        protocol (str, optional): Protocol to access by URI. Defaults to "http".
        dir_point (list, optional): Directory point to access with URI. Defaults to [''].
        data_template (dict, optional): Template data to generate and use for POST Request. Defaults to {"name":"HelloWorld!!!"}.
        set_timeout (float, optional): Timeout to exit process. Defaults to 5.0.
        sleep_timeout (int, optional): Time out to sleep. Defaults to 2.
    
    Returns:
        dict: The dictionary containing the processed during the interaction
            {
                "Total Request": (int),
                "2xx Response": (int),
                "3xx Response": (int),
                "4xx Response": (int),
                "5xx Response": (int)
            }
    """ 
    
    results_interact = { "Total Request": 0, "2xx Response": 0, "3xx Response": 0, "4xx Response": 0, "5xx Response": 0 }
    type_value_dict_key = [type(data_template[key]).__name__ for key in list(data_template.keys())]
    dict_key = list(data_template.keys())
    while set_timeout > 0:
        start_time = time.time()
        pick_one = random.choice(method)
        pick_dir = random.choice(dir_point)
        if pick_one == "GET":
            response = requests.get(url=protocol + "://" + location_uri + ":" + port + pick_dir)
            if response.status_code == 200:
                results_interact["Total Request"] = results_interact["Total Request"] + 1
                results_interact["2xx Response"] = results_interact["2xx Response"] + 1
            if response.status_code == 300:
                results_interact["Total Request"] = results_interact["Total Request"] + 1
                results_interact["3xx Response"] = results_interact["3xx Response"] + 1
            if response.status_code == 400:
                results_interact["Total Request"] = results_interact["Total Request"] + 1
                results_interact["4xx Response"] = results_interact["4xx Response"] + 1
            if response.status_code == 500:
                results_interact["Total Request"] = results_interact["Total Request"] + 1
                results_interact["5xx Response"] = results_interact["5xx Response"] + 1
        if pick_one == "POST":
            if pick_dir == "/":
                time.sleep(sleep_timeout)
                end_time = time.time()
                set_timeout -= end_time - start_time  
                print(set_timeout)      
                continue
            else:
                value_generate = [generate_random_todo(x) for x in type_value_dict_key]
                dict_generate = {dict_key[i]:value_generate[i] for i in range(len(dict_key))}
                response = requests.post(url=protocol + "://" + location_uri + ":" + port + pick_dir,
                                headers={"Content-Type":"application/json"}, data=json.dumps(dict_generate))
                if response.status_code == 200:
                    results_interact["Total Request"] = results_interact["Total Request"] + 1
                    results_interact["2xx Response"] = results_interact["2xx Response"] + 1
                if response.status_code == 300:
                    results_interact["Total Request"] = results_interact["Total Request"] + 1
                    results_interact["3xx Response"] = results_interact["3xx Response"] + 1
                if response.status_code == 400:
                    results_interact["Total Request"] = results_interact["Total Request"] + 1
                    results_interact["4xx Response"] = results_interact["4xx Response"] + 1
                if response.status_code == 500:
                    results_interact["Total Request"] = results_interact["Total Request"] + 1
                    results_interact["5xx Response"] = results_interact["5xx Response"] + 1
        if pick_one == "PUT":
            if pick_dir == "/":
                time.sleep(sleep_timeout)
                end_time = time.time()
                set_timeout -= end_time - start_time
                print(set_timeout)  
                continue
            else:
                response = requests.get(url=protocol + "://" + location_uri + ":" + port + pick_dir)
                if len(response.json()) == 0:
                    if "POST" in method:
                        time.sleep(sleep_timeout)
                        end_time = time.time()
                        set_timeout -= end_time - start_time
                        print(set_timeout)  
                        continue
                    else:
                        print("Not have anything, force stop to do anything")
                        set_timeout = 0
                        break
                        
                if len(response.json()) >= 1:
                    object_random = random.choice(response.json())
                    if object_random['completed'] == False:
                        dict_parse = {"name": object_random['name'], "completed": True}
                        response = requests.put(url=protocol + "://" + location_uri + ":" + port + pick_dir + "/" + object_random["id"], 
                                        headers={"Content-Type":"application/json"}, data=json.dumps(dict_parse))
                        if response.status_code == 200:
                            results_interact["Total Request"] = results_interact["Total Request"] + 2
                            results_interact["2xx Response"] = results_interact["2xx Response"] + 2
                        if response.status_code == 300:
                            results_interact["Total Request"] = results_interact["Total Request"] + 2
                            results_interact["2xx Response"] = results_interact["2xx Response"] + 1
                            results_interact["3xx Response"] = results_interact["3xx Response"] + 1
                        if response.status_code == 400:
                            results_interact["Total Request"] = results_interact["Total Request"] + 2
                            results_interact["2xx Response"] = results_interact["2xx Response"] + 1
                            results_interact["4xx Response"] = results_interact["4xx Response"] + 1
                        if response.status_code == 500:
                            results_interact["Total Request"] = results_interact["Total Request"] + 2
                            results_interact["2xx Response"] = results_interact["2xx Response"] + 1
                            results_interact["5xx Response"] = results_interact["5xx Response"] + 1
                    if object_random['completed'] == True:
                        dict_parse = {"name": object_random['name'], "completed": False}
                        response = requests.put(url=protocol + "://" + location_uri + ":" + port + pick_dir + "/" + object_random["id"], 
                                        headers={"Content-Type":"application/json"}, data=json.dumps(dict_parse))
                        if response.status_code == 200:
                            results_interact["Total Request"] = results_interact["Total Request"] + 2
                            results_interact["2xx Response"] = results_interact["2xx Response"] + 2
                        if response.status_code == 300:
                            results_interact["Total Request"] = results_interact["Total Request"] + 2
                            results_interact["2xx Response"] = results_interact["2xx Response"] + 1
                            results_interact["3xx Response"] = results_interact["3xx Response"] + 1
                        if response.status_code == 400:
                            results_interact["Total Request"] = results_interact["Total Request"] + 2
                            results_interact["2xx Response"] = results_interact["2xx Response"] + 1
                            results_interact["4xx Response"] = results_interact["4xx Response"] + 1
                        if response.status_code == 500:
                            results_interact["Total Request"] = results_interact["Total Request"] + 2
                            results_interact["2xx Response"] = results_interact["2xx Response"] + 1
                            results_interact["5xx Response"] = results_interact["5xx Response"] + 1
        if pick_one == "DELETE":
            if pick_dir == "/":
                time.sleep(sleep_timeout)
                end_time = time.time()
                set_timeout -= end_time - start_time
                print(set_timeout)  
                continue
            else:
                response = requests.get(url=protocol + "://" + location_uri + ":" + port + pick_dir)
                if len(response.json()) == 0:
                    if "POST" in method:
                        time.sleep(sleep_timeout)
                        end_time = time.time()
                        set_timeout -= end_time - start_time
                        print(set_timeout)  
                        continue
                    else:
                        print("Not have anything, force stop to do anything")
                        set_timeout = 0
                        break
                if len(response.json()) >= 1:
                    object_random = random.choice(response.json())
                    response = requests.delete(url=protocol + "://" + location_uri + ":" + port + pick_dir +"/" + object_random['id'])
                    if response.status_code == 200:
                        results_interact["Total Request"] = results_interact["Total Request"] + 2
                        results_interact["2xx Response"] = results_interact["2xx Response"] + 2
                    if response.status_code == 300:
                        results_interact["Total Request"] = results_interact["Total Request"] + 2
                        results_interact["2xx Response"] = results_interact["2xx Response"] + 1
                        results_interact["3xx Response"] = results_interact["3xx Response"] + 1
                    if response.status_code == 400:
                        results_interact["Total Request"] = results_interact["Total Request"] + 2
                        results_interact["2xx Response"] = results_interact["2xx Response"] + 1
                        results_interact["4xx Response"] = results_interact["4xx Response"] + 1
                    if response.status_code == 500:
                        results_interact["Total Request"] = results_interact["Total Request"] + 2
                        results_interact["2xx Response"] = results_interact["2xx Response"] + 1
                        results_interact["5xx Response"] = results_interact["5xx Response"] + 1
        time.sleep(sleep_timeout)
        end_time = time.time()
        set_timeout -= end_time - start_time
        print(set_timeout)  
    return results_interact
            
def benchmark_todo(location_uri = "localhost", port = "80",  protocol = "http", 
                   dir_point = "/items", set_timeout=5, worker=10, number_requests=1000):
    """
    Doing a benchmark with a ab (Apache Benchmark) tools

    Args:
        location_uri (str, optional): URI to benchmark. Defaults to "localhost".
        port (str, optional): Port to put with URI. Defaults to "80".
        protocol (str, optional): Protocol to access. Defaults to "http".
        dir_point (str, optional): Directory Point to benchmark. Defaults to "/items".
        set_timeout (int, optional): Time out ab set to benchmark. Defaults to 5.
        worker (int, optional): Number of worker to do the job request. Defaults to 10.
        number_requests (int, optional): Number of request. Defaults to 1000.
    """
    
    os.system("ab" + " -n " + str(number_requests) + " -c " + str(worker) + " -t " 
              + str(set_timeout) + " " + protocol + "://" + location_uri + ":" + port + dir_point)


def __main__():
    """Main function to interact with another function created above
    """    
    TYPE = ['interact', 'benchmark']
    parser = argparse.ArgumentParser(description="Bot for request to web with purpose do [Interact or Benchmark]")
    parser.add_argument('-T', '--type', help='purpose of type for doing with bot', choices=TYPE, required=True)
    parser.add_argument('-P', '--protocol', help='protocol of request', default="http")
    parser.add_argument('-l', '--location_uri', help='URI for request', required=True)
    parser.add_argument('-p', '--port', help='port of URI to request', default="80")
    parser.add_argument('-m', '--method', help='method of request', nargs='+', required=TYPE[0] in argv)
    parser.add_argument('-d', '--directory', help='directory of request [More with interact but specify with benchmark]', nargs='+', required=True)
    parser.add_argument('-t', '--timeout', help='timoout give for bot in (seconds) [Valid with both mode]', type=int, default=30)
    parser.add_argument('-s', '--sleep', help='seconds to sleep for each request [Valid with interact Mode]', type=int, default=5)
    parser.add_argument('-D', '--data_templates', help='Data templates for post requests [Valid with interact Mode]' + 
                                'Type: Dictionary. Example: {"name":"HelloWorld!!!"} ', type=dict, default={"name":"HelloWorld!!!"})
    parser.add_argument('-w', '--workers', help='Number of workers or concurence level for doing a job', default=10)
    parser.add_argument('--number_requests', help='Number of requests for benchmarking', default=1000)
    opt = parser.parse_args()

    timeout = opt.timeout
    protocol = opt.protocol
    location_uri = opt.location_uri
    port = opt.port
    directory = [str(d) for d in opt.directory]
    if opt.type == "interact":
        method = [str(m) for m in opt.method]
        template = opt.data_templates
        sleep_timeout = opt.sleep
        results_interact = interact_todo(method=method, location_uri=location_uri, port=port, protocol=protocol, dir_point=directory,
                                         data_template=template, set_timeout=float(timeout), sleep_timeout=sleep_timeout)
        print('Processing results: Succeed after ' + str(datetime.timedelta(seconds=timeout)) + "\n" + 
              "Results:" + "\n" +
              "\t- Total Requests: " + str(results_interact["Total Request"]) + "\n" +
              "\t- Total 2xx Response: " + str(results_interact["2xx Response"]) + "\n" +
              "\t- Total 3xx Response: " + str(results_interact["3xx Response"]) + "\n" +
              "\t- Total 4xx Response: " + str(results_interact["4xx Response"]) + "\n" +
              "\t- Total 5xx Response: " + str(results_interact["5xx Response"]) + "\n")
    if opt.type == "benchmark":
        if len(directory) != 1:
            print("Multiple directories not supported for benchmark version, please specify the directory")
        if len(directory) == 1:
            benchmark_todo(location_uri=location_uri, port=port, protocol=protocol, dir_point=directory[0], 
                           set_timeout=timeout, worker=opt.workers, number_requests=opt.number_requests) 
        
if __name__=='__main__':
    __main__()
