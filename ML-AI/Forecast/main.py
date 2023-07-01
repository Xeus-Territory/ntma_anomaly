import concurrent.futures
import requests
import schedule
import logging
import time
import json
import os

from redis.connection import ConnectionPool
from datetime import datetime, timedelta
from dotenv import load_dotenv
from redis import Redis

import pandas as pd
import numpy as np

load_dotenv()

PROMETHEUS_HOSTNAME = '209.97.168.207'
PROMETHEUS_PORT = 9090
REDIS_HOSTNAME = '209.97.168.207'
REDIS_PORT = 6379

data_metrics = {
    "service_avg_cpu_usage_percentage": 0,
    "service_avg_memory_usage_percentage": 0,
    "nginx_avg_respone_time": 0,
    "nginx_requests_per_second": 0
}

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Check if the root logger does not have a StreamHandler, then add a new one.
if not logging.getLogger('').handlers:
    # Add a StreamHandler to log messages to the console.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logging.getLogger('').addHandler(console_handler)


class RedisConnection:
    def __init__(self):
        redis_pool = ConnectionPool(host=REDIS_HOSTNAME, port=REDIS_PORT, db=0)
        self.connection = Redis(connection_pool=redis_pool)

    def add_metrics_to_redis(self, key, data):
        try:
            self.connection.lpush(key, json.dumps(data))
            self.connection.expire(key, 259200)
            logging.info(f"Data added successfully with key '{key}'")
        except Exception as e:
            logging.error(f"Error processing message: {e}")


def get_metrics(metric1, metric2):
    try:
        api_url = (
            f'http://{PROMETHEUS_HOSTNAME}:{PROMETHEUS_PORT}/api/v1/query?'
            f'query={{__name__=~"{metric1}|{metric2}"}}'
        )
            
        response = requests.get(api_url, timeout=2)
        if response.status_code == 200:
            data = response.json()

            if 'data' in data and 'result' in data['data']:
                result = data['data']['result']
                if len(result) > 0:
                    values_by_name = {}

                    for item in result:
                        name = item['metric']['__name__']
                        value = item['value'][1]
                        values_by_name[name] = value

                    return (
                        values_by_name[metric1],
                        values_by_name[metric2]
                    )

    except Exception as e:
        logging.error(f"Error processing message: {e}")
        
    return 0, 0

import glob

folder_path_1 = './2023-06-20/'
folder_path_2 = './2023-06-21/'
folder_path_3 = './2023-06-22/'

folder_paths = [folder_path_1, folder_path_2, folder_path_3]

csv_files = []
dataframes = []

for folder_path in folder_paths:
    folder_csv_files = sorted(glob.glob(folder_path + '*.csv'))
    csv_files.extend(folder_csv_files)

    for file in folder_csv_files:
        df = pd.read_csv(file)
        dataframes.append(df)

df = pd.concat(dataframes, ignore_index=True)

df['time'] = pd.to_datetime(df['time'])

df1 = pd.DataFrame(df, columns=['time',
                                'service_avg_cpu_usage_percentage',
                                'service_avg_memory_usage_percentage', 
                                'nginx_avg_respone_time', 
                                'nginx_requests_per_second'
                                ])
df1.index=df1["time"]
df1.drop("time", axis=1, inplace=True)

df1['nginx_avg_respone_time'] = df1['nginx_avg_respone_time'].fillna(0)

def df_to_X_y(df, window_size=7):
  df_as_np = df.to_numpy()
  X = []
  y = []
  for i in range(len(df_as_np)-window_size):
    row = [r for r in df_as_np[i:i+window_size]]
    X.append(row)
    label = [df_as_np[i+window_size][0], df_as_np[i+window_size][1], df_as_np[i+window_size][2], df_as_np[i+window_size][3]]
    y.append(label)
  return np.array(X), np.array(y)

window_size = 30
X, y = df_to_X_y(df1, window_size)

train_size = int(len(X)*0.7)
val_size = int(len(X)*0.15)
# test_size = len(X) - train_size - val_size

X_train, y_train = X[:train_size], y[:train_size]
X_val, y_val = X[train_size: (train_size + val_size)], y[train_size: (train_size + val_size)]
X_test, y_test = X[(train_size + val_size):], y[(train_size + val_size):]

# print(X_train.shape, y_train.shape, X_val.shape, y_val.shape, X_test.shape, y_test.shape)
# When each retrain, we need using other variable, if success -> load new with value, else -> skip

cpu_training_mean = np.mean(X_train[:, :, 0])
cpu_training_std = np.std(X_train[:, :, 0])

ram_training_mean = np.mean(X_train[:, :, 1])
ram_training_std = np.std(X_train[:, :, 1])

nginx_avg_respone_time_training_mean = np.mean(X_train[:, :, 2])
nginx_avg_respone_time_training_std = np.std(X_train[:, :, 2])

nginx_requests_per_second_training_mean = np.mean(X_train[:, :, 3])
nginx_requests_per_second_training_std = np.std(X_train[:, :, 3])

def preprocess(X):
    X[:, :, 0] = (X[:, :, 0] - cpu_training_mean) / cpu_training_std
    X[:, :, 1] = (X[:, :, 1] - ram_training_mean) / ram_training_std
    X[:, :, 2] = (X[:, :, 2] - nginx_avg_respone_time_training_mean) / nginx_avg_respone_time_training_std
    X[:, :, 3] = (X[:, :, 3] - nginx_requests_per_second_training_mean) / nginx_requests_per_second_training_std

def preprocess_output(y):
    y[:, 0] = (y[:, 0] - cpu_training_mean) / cpu_training_std
    y[:, 1] = (y[:, 1] - ram_training_mean) / ram_training_std
    y[:, 2] = (y[:, 2] - nginx_avg_respone_time_training_mean) / nginx_avg_respone_time_training_std
    y[:, 3] = (y[:, 3] - nginx_requests_per_second_training_mean) / nginx_requests_per_second_training_std
    return y

from tensorflow.keras.models import load_model

final_model=load_model('save_model.hdf5')

def postprocess_cpu(arr):
  arr = (arr*cpu_training_std) + cpu_training_mean
  return arr

def postprocess_ram(arr):
  arr = (arr*ram_training_std) + ram_training_mean
  return arr


def postprocess_nginx_avg_res(arr):
  arr = (arr*nginx_avg_respone_time_training_std) + nginx_avg_respone_time_training_mean
  return arr

def postprocess_nginx_req_per(arr):
  arr = (arr*nginx_requests_per_second_training_std) + nginx_requests_per_second_training_mean
  return arr

def worker1():
    global data_metrics

    metric1 = 'nginx_avg_respone_time'
    metric2 = 'nginx_requests_per_second'

    (
        data_metrics["nginx_avg_respone_time"],
        data_metrics["nginx_requests_per_second"],
    ) = get_metrics(metric1, metric2)


def worker2():
    global data_metrics

    metric1 = 'service_avg_cpu_usage_percentage'
    metric2 = 'service_avg_memory_usage_percentage'

    (
        data_metrics["service_avg_cpu_usage_percentage"],
        data_metrics["service_avg_memory_usage_percentage"]
    ) = get_metrics(metric1, metric2)


list_arr_3d = []

def worker3():
    global data_metrics, df1_new, list_arr_3d

    datetime_object = datetime.now()
    new_datetime_object = datetime_object - timedelta(seconds=5)
    key = new_datetime_object.strftime("%Y-%m-%d-%H")

    time = new_datetime_object.strftime("%Y-%m-%dT%H:%M:%S")

    metrics = data_metrics
    for key in metrics:
        if metrics[key] != 'NaN':
            metrics[key] = float(metrics[key])
        else:
            metrics[key] = 0.0

    print(time)
    print(metrics)

    df1_new = pd.concat([df1_new, pd.DataFrame(metrics, index=[0])], ignore_index=True).drop(0)
    df1_new = df1_new.reset_index(drop=True)

    df1_tmp = df1_new.copy()

    # arr_2d = np.zeros((rows_2d, cols_2d))
    l_2d = []

    for i in range(0, 12):
        data_X, data_y = df_to_X_y(df1_tmp, 30)
        preprocess(data_X)
        # preprocess_output(data_y)
        predictions = final_model.predict(data_X)
        data_predictions = pd.DataFrame(data={'service_avg_cpu_usage_percentage':postprocess_cpu(predictions[:, 0]),
                                            'service_avg_memory_usage_percentage':postprocess_ram(predictions[:, 1]),
                                            'nginx_avg_respone_time':postprocess_nginx_avg_res(predictions[:, 2]),
                                            'nginx_requests_per_second':postprocess_nginx_req_per(predictions[:, 3])})
        # arr_2d[i] = data_predictions
        l_2d.append(data_predictions.values.tolist()[0])
        df1_tmp = pd.concat([df1_tmp, data_predictions], ignore_index=True).drop(0)
        df1_tmp = df1_tmp.reset_index(drop=True)
    
    print("OK", datetime.now())
    print(df1_new)
    print(df1_tmp)
    # numpy_array = np.array(l_2d)
    # print(numpy_array)
    print(l_2d)
    print("=======================")
    # print(arr_2d.shape[0], arr_2d.shape[1])

    if (len(list_arr_3d) > 12):
        del list_arr_3d[0]
    if (len(list_arr_3d) == 12):
        print("Tinh do lech.")
        # numpy_array = np.array(list_arr_3d)
        list_tmp = [metrics['service_avg_cpu_usage_percentage'], metrics['service_avg_memory_usage_percentage'],
              metrics["nginx_avg_respone_time"], metrics["nginx_requests_per_second"]]
        print(list_tmp)
        # print(numpy_array)
        # print(list_arr_3d)
        l_cal = []
        size = len(list_arr_3d)
        for i in range(0, size):
            # print(list_arr_3d[i][size - i -1])
            l_cal.append(list_arr_3d[i][size - i -1])
        
        percentage_deviations = []
        countDeviation = 0  # Variable that counts the number of elements with a deviation greater than 20%

        for sublist in l_cal:
            deviations = [abs(x - y) for x, y in zip(list_tmp, sublist)]
            percentage_deviation = [(dev / orig) * 100 for dev, orig in zip(deviations, list_tmp)]
            percentage_deviations.append(percentage_deviation)

            count = 0
            for deviation in percentage_deviation:
                if deviation > 20:
                    count += 1
            if count > (len(percentage_deviation) / 2):
                countDeviation += 1

        print("The number of elements with a deviation greater than 20%:", countDeviation)
    list_arr_3d.append(l_2d)
        
    # redis_connection.add_metrics_to_redis(key, data_metrics)
    # print(list_arr_2d)

def run_worker1():
    schedule.every(3).seconds.do(worker1)
    return schedule.CancelJob


def run_worker2():
    schedule.every(3).seconds.do(worker2)
    return schedule.CancelJob


def run_worker3():
    schedule.every(10).seconds.do(worker3)
    return schedule.CancelJob

data_new = pd.read_csv('2023-06-23-00.csv')
df_new = pd.concat([data_new['service_avg_cpu_usage_percentage'], 
                    data_new['service_avg_memory_usage_percentage'],
                    data_new['nginx_avg_respone_time'], 
                    data_new['nginx_requests_per_second']], axis=1)
df1_new = df_new[:31].copy()

if __name__ == '__main__':
    redis_connection = RedisConnection()

    pool = concurrent.futures.ThreadPoolExecutor(max_workers=3)



    pool.submit(run_worker1)
    pool.submit(run_worker2)
    pool.submit(run_worker3)

    logging.info("Main thread continuing to run")
    while True:
        schedule.run_pending()
        time.sleep(1)
