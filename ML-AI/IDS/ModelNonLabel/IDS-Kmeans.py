import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from user_agents import parse
from sklearn.cluster import KMeans
from sklearn.utils import shuffle
import warnings
warnings.filterwarnings('ignore')
from sklearn.metrics import silhouette_score
import schedule
import requests
from dotenv import load_dotenv
import os
from kafka import KafkaConsumer
import re
import threading
from concurrent.futures import ThreadPoolExecutor
import time

# Load the environment variable
load_dotenv()
IP_MANAGER = os.environ.get('IP_MANAGER')
OPENPORT = os.environ.get('OPENPORT')
PROMETHEUS_HOSTNAME= os.environ.get('PROMETHEUS_HOSTNAME')
PROMETHEUS_PORT= os.environ.get("PROMETHEUS_PORT")
KAFKA_HOSTNAME= os.environ.get('KAFKA_HOSTNAME')
KAFKA_PORT= os.environ.get('KAFKA_PORT')
KAFKA_TOPIC= os.environ.get('KAFKA_TOPIC')

# Initialize kafka consumer instance
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=f"{KAFKA_HOSTNAME}:{KAFKA_PORT}",
    auto_offset_reset='latest',
    max_poll_records=1000
)

# Initialize log regex
reg_log_pattern = re.compile(
    r'\"(?P<remote_addr>[^"]+)\"\s'
    r'\"(?P<remote_usr>[^"]+)\"\s'
    r'\"(?P<time_local>[^"]+)\"\s'
    r'\"(?P<request_method>[A-Z]+)\s'
    r'(?P<request_url>[^"]+)\s'
    r'(?P<http_version>HTTP/\d\.\d)\"\s'
    r'\"(?P<status>[^"]+)\"\s'
    r'\"(?P<body_bytes_sent>[^"]+)\"\s'
    r'\"(?P<http_referer>[^"]+)\"\s'
    r'\"(?P<http_user_agent>[^"]+)\"\s'
    r'\"(?P<http_x_forwarded_for>[^"]+)\"\s'
    r'\"(?P<request_length>[^"]+)\"\s'
    r'\"(?P<request_time>[^"]+)\"\s'
    r'\"(?P<upstream_response_time>[^"]+)\"\s'
)

        
## Initialize the param for training 
PATH_TRAIN_DATA = '../../Data/Collection/data_raw.csv'
PATH_RESULT = '../../Data/Collection/result_kmeans.csv'
FIREWALL_FLAG = False
RETRAIN_FLAG = False
MODEL_AVAILABLE = False
MODEL = KMeans()
SCORE_TRAIN = 0
DF_TRAIN = pd.DataFrame()
DF_PREDICTION = pd.DataFrame()
PREDICT_LABEL = []
AVAILABLE_PREDICT_LABEL = True
NUMBER_OF_NORMAL_TRAIN = 0
NUMBER_OF_ATTACK_TRAIN = 0
NUMBER_OF_BENCHMARK_TRAIN = 0
NUMBER_OF_NORMAL_PREDICT = 0
NUMBER_OF_ATTACK_PREDICT = 0
NUMBER_OF_BENCHMARK_PREDICT = 0

def initialize_input(data):
    """initialize the template input for input data to predict process

    Args:
        data (dataframe): convert to raw data collection topic from kafka into dataframe
    """
    path = PATH_TRAIN_DATA
    template_columns = pd.read_csv(path).columns
    DF_INPUT = pd.DataFrame(columns=list(template_columns))
    DF_INPUT.loc[0] = data
    return DF_INPUT
    

def initialize_template(type):
    """initialize the template data for re-train dataframe with density
    """    
    global DF_PREDICTION, DF_TRAIN
    path = ""
    template_columns = []
    if type == 'train':
        path = PATH_TRAIN_DATA
        template_columns = list(pd.read_csv(path).columns)
        DF_PREDICTION = pd.DataFrame(columns=template_columns)
    if type == 'predict':
        path = PATH_RESULT
        template_columns = list(pd.read_csv(path).columns)
        DF_PREDICTION = pd.DataFrame(columns=list(template_columns))  
        
def density_decision(amount_request):
    """Check the density of ratio between normal and abnormal requests rates
    """    
    global FIREWALL_FLAG, NUMBER_OF_ATTACK_PREDICT, NUMBER_OF_BENCHMARK_PREDICT, NUMBER_OF_NORMAL_PREDICT
    try:
        total = NUMBER_OF_ATTACK_PREDICT + NUMBER_OF_BENCHMARK_PREDICT + NUMBER_OF_NORMAL_PREDICT
        if total >= amount_request:
            # Idea: if the number of normal requests have density >= 80 % (NORMAL)
            #       if the number of normal requests have density < 80 % (ABNORMAL)
            density = (NUMBER_OF_NORMAL_PREDICT / total)
            if density >= 0.8:
                if FIREWALL_FLAG == True:
                    FIREWALL_FLAG = False
                    requests.post('http://' + str(IP_MANAGER) + ":" + str(OPENPORT) + "/security_info?density={density}".format(density=density))
                    requests.post('http://'+ str(IP_MANAGER) + ":" + str(OPENPORT) + "/firewall?state=down")
                    NUMBER_OF_ATTACK_PREDICT = 0
                    NUMBER_OF_BENCHMARK_PREDICT = 0
                    NUMBER_OF_NORMAL_PREDICT = 0
                    return
                if FIREWALL_FLAG == False:
                    print("Nothing to change here")
            else:
                if FIREWALL_FLAG == False:
                    FIREWALL_FLAG = True
                    requests.post('http://' + str(IP_MANAGER) + ":" + str(OPENPORT) + "/security_info?density={density}".format(density=density))
                    requests.post('http://'+ str(IP_MANAGER) + ":" + str(OPENPORT) + "/firewall?state=up")
                    NUMBER_OF_ATTACK_PREDICT = 0
                    NUMBER_OF_BENCHMARK_PREDICT = 0
                    NUMBER_OF_NORMAL_PREDICT = 0
                    return
                if FIREWALL_FLAG == True:
                    print("Nothing to change here")     
        else:
            pass
    except Exception as e:
        print("Error: " + str(e))
        pass


def preprocess_data(df_raw):
    """Pre-precessing for raw data to convert that into the expected format

    Args:
        df_raw (data_frame): data raw representation for log convert into csv

    Returns:
        dataframe: data after preprocessing and encoding features of data
    """   
    df = df_raw
    ## Drop poor feature - to easy for converting
    columes_with_non_unique = []
    for column in df.columns:
        # print("{column} with {unique} unique value".format(column=column, unique=len(df[column].unique())))
        if (len(df[column].unique()) == 1):
            columes_with_non_unique.append(column)
    columes_with_non_unique.append("http_referer")
    columes_with_non_unique.append("time_local")
    df = df.drop(columns=columes_with_non_unique)
    
    ## feature-engineering for feature to data can understand
    ## Process request-method: using one hot lable encoding
    enc_data = pd.get_dummies(df['request_method']).astype('Int64')
    df = df.join(enc_data)
    df = df.drop(columns=['request_method'])
    
    ## Process url-status: using labeling encoding
    available_request = []
    error_request = []
    for i in df['status']:
        if i >= 100 and i <= 399:
            available_request.append(1)
            error_request.append(0)
        elif i >= 400 and i <= 599:
            available_request.append(0)
            error_request.append(1)
            
    df['available_request'] = available_request
    df['error_request'] = error_request
    df = df.drop(columns=['request_url', 'status'])
    
    ## Process http_version: using one hot lable encoding
    enc_data = pd.get_dummies(df['http_version']).astype('Int64')
    df = df.join(enc_data)
    df = df.drop(columns=['http_version'])
    
    ## Process http_user_agent: using labelling encoding
    valid_user_agent = []
    supicious_user_agent = []
    for agent in df['http_user_agent']:
        user_agent = parse(agent)
        if user_agent.is_pc or user_agent.is_mobile:
            valid_user_agent.append(1)
            supicious_user_agent.append(0)
        else:
            valid_user_agent.append(0)
            supicious_user_agent.append(1)

    df['valid_user_agent'] = valid_user_agent
    df['supicious_user_agent'] = supicious_user_agent
    df = df.drop(columns=['http_user_agent'])
    
    ## Fill na when situation request return 4xx and 5xx cannot have enough data
    df = df.replace("-", 0)
    
    return df

def preprocess_data_V2(df_raw):
    """Pre-precessing for raw data to convert that into the expected format

    Args:
        df_raw (data_frame): data raw representation for log convert into csv

    Returns:
        dataframe: data after preprocessing and encoding features of data
    """   
    df = df_raw
    ## Drop poor feature - to easy for converting
    columes_with_non_unique = []
    columes_with_non_unique.append("remote_usr")
    columes_with_non_unique.append("remote_addr")
    columes_with_non_unique.append("http_referer")
    columes_with_non_unique.append("time_local")
    columes_with_non_unique.append("http_x_forwarded_for")
    df = df.drop(columns=columes_with_non_unique)
    
    ## feature-engineering for feature to data can understand
    ## Process request-method: using one hot lable encoding
    GET = []
    POST = []
    PUT = []
    DELETE = []
    for method in df['request_method']:
        if method == 'POST':
            GET.append(0)
            POST.append(1)
            PUT.append(0)
            DELETE.append(0)
        if method == 'GET':
            GET.append(1)
            POST.append(0)
            PUT.append(0)
            DELETE.append(0)
        if method == 'DELETE':
            GET.append(0)
            POST.append(0)
            PUT.append(0)
            DELETE.append(1)
        if method == "PUT":
            GET.append(0)
            POST.append(0)
            PUT.append(1)
            DELETE.append(0)
    df['DELETE'] = DELETE
    df['GET'] = GET
    df['POST'] = POST
    df['PUT'] = PUT 
    df = df.drop(columns=['request_method'])
    
    ## Process url-status: using labeling encoding
    available_request = []
    error_request = []
    for i in df['status']:
        if i >= 100 and i <= 399:
            available_request.append(1)
            error_request.append(0)
        elif i >= 400 and i <= 599:
            available_request.append(0)
            error_request.append(1)
            
    df['available_request'] = available_request
    df['error_request'] = error_request
    df = df.drop(columns=['request_url', 'status'])
    
    ## Process http_version: using one hot lable encoding
    HTTP_10 = []
    HTTP_11 = []
    for version in df['http_version']:
        if version == "HTTP/1.0":
            HTTP_10.append(1)
            HTTP_11.append(0)
        if version == "HTTP/1.1":
            HTTP_11.append(1)
            HTTP_10.append(0)
    df['HTTP/1.0'] = HTTP_10
    df['HTTP/1.1'] = HTTP_11
    df = df.drop(columns=['http_version'])
    
    ## Process http_user_agent: using labelling encoding
    valid_user_agent = []
    supicious_user_agent = []
    for agent in df['http_user_agent']:
        user_agent = parse(agent)
        if user_agent.is_pc or user_agent.is_mobile:
            valid_user_agent.append(1)
            supicious_user_agent.append(0)
        else:
            valid_user_agent.append(0)
            supicious_user_agent.append(1)

    df['valid_user_agent'] = valid_user_agent
    df['supicious_user_agent'] = supicious_user_agent
    df = df.drop(columns=['http_user_agent'])
    
    ## Fill na when situation request return 4xx and 5xx cannot have enough data
    df = df.replace("-", 0)
    
    return df

def post_processing(df_predict):
    """Post Processing of data after prediction about assign label and fix actually right situations

    Args:
        df_predict (dataframe): dataframe after prediction by model and assigned label by model AI

    Returns:
        dataframe: new dataframe after post-processiong and fix correction situation
    """   
    df = df_predict
    # Change label base on the assign number (Just random pick incase - Not important)
    df.loc[(df['cluster_kmeans'] == 1), ['cluster_kmeans']] = "normal"
    df.loc[(df['cluster_kmeans'] == 3), ['cluster_kmeans']] = "webattack"
    df.loc[(df['cluster_kmeans'] == 2), ['cluster_kmeans']] = "benchmark"
    
    # Change label cluster info base on the knowledge (Base on analysis graph - decision partition for 3 type of request)
    df.loc[(df['request_time'] <= 0.2) & (df['network_receive_bytes_per_second'] <= 1900000), ['cluster_kmeans']] = "normal"
    df.loc[((df['request_time'] > 0.2) & (df['network_receive_bytes_per_second'] <= 3500000)) | ((df['network_receive_bytes_per_second'] > 1900000) & (df['network_receive_bytes_per_second'] <= 3500000)), ['cluster_kmeans']] = "webattack"
    df.loc[(df['network_receive_bytes_per_second'] > 3500000), ['cluster_kmeans']] = "benchmark"
    
    # Fix the situation need to right
    df.loc[(df['valid_user_agent'] == 1) & (df['available_request'] == 1), ['cluster_kmeans']] = "normal"
    df.loc[(df['valid_user_agent'] == 0) & (df['available_request'] == 0), ['cluster_kmeans']] = "webattack"
    df.loc[(df['valid_user_agent'] == 1) & (df['available_request'] == 0), ['cluster_kmeans']] = "webattack"
    
    return df

def calculate_score_model(df_preprocess):
    """Calculator the score of model Kmean base on euclidean distance

    Args:
        df_preprocess (dataframe): DataFrame after preprocess
    """    
    global SCORE_TRAIN,MODEL
    SCORE_TRAIN = silhouette_score(df_preprocess, MODEL.predict(df_preprocess))
    print("Scoring of current model KMEANs: ", SCORE_TRAIN)

def kmeans_model_train(df_raw):
    """Building a kmeans for trainning process

    Args:
        df_preprocess (_type_): _description_
        
    """ 
    global MODEL, SCORE_TRAIN, NUMBER_OF_NORMAL_TRAIN, NUMBER_OF_ATTACK_TRAIN, NUMBER_OF_BENCHMARK_TRAIN, MODEL_AVAILABLE
    MODEL_AVAILABLE = False   
    df = preprocess_data(df_raw)
    
    # KMeans
    kmean3 = KMeans(n_clusters=3, verbose=1)
    kmean3.fit(df)
    MODEL = kmean3
    threading.Thread(target=calculate_score_model, kwargs={'df_preprocess': df}).start()
    
    y_pred = MODEL.fit_predict(df)
    df['cluster_kmeans'] = y_pred+1
    
    # Post-process for dataframe
    df = post_processing(df)
    
    # Statictis the label
    # NUMBER_OF_NORMAL_TRAIN = df['cluster_kmeans'].value_counts()['normal']
    # NUMBER_OF_ATTACK_TRAIN = df['cluster_kmeans'].value_counts()['webattack']
    # NUMBER_OF_BENCHMARK_TRAIN = df['cluster_kmeans'].value_counts()['benchmark']
    
    # Update the state of Available Flag
    MODEL_AVAILABLE = True 
    print("Successfully build and ready for receive queue message from kafka cluster")

def kmeans_predict(df_raw):
    """Prediction for each log through by message queue from kafka

    Args:
        raw (list): Raw data pass for prediction proccess from kafka 
    """    
    global NUMBER_OF_NORMAL_PREDICT, NUMBER_OF_BENCHMARK_PREDICT, NUMBER_OF_ATTACK_PREDICT, DF_PREDICTION, MODEL, PREDICT_LABEL, AVAILABLE_PREDICT_LABEL
    DF_PREDICTION = pd.concat([DF_PREDICTION, df_raw], ignore_index= True)
    df = preprocess_data_V2(df_raw)
    y_pred = MODEL.predict(df)
    df['cluster_kmeans'] = y_pred+1
    df = post_processing(df)
    state_req = df['cluster_kmeans'].values[0]
    print(state_req)
    while True:
        if AVAILABLE_PREDICT_LABEL == True:
            AVAILABLE_PREDICT_LABEL = False
            if state_req == "normal":
                PREDICT_LABEL.append(0)
                NUMBER_OF_NORMAL_PREDICT = NUMBER_OF_NORMAL_PREDICT + 1
            if state_req == "webattack":
                PREDICT_LABEL.append(1)
                NUMBER_OF_ATTACK_PREDICT = NUMBER_OF_ATTACK_PREDICT + 1
            if state_req == "benchmark":
                PREDICT_LABEL.append(3)
                NUMBER_OF_BENCHMARK_PREDICT = NUMBER_OF_BENCHMARK_PREDICT + 1
            AVAILABLE_PREDICT_LABEL = True
            break
        if AVAILABLE_PREDICT_LABEL == False:
            continue
        
        
def validate_model():
    """
        Validate the model base on silhouette score for give evaluation for curren model
    """    
    global SCORE_TRAIN, DF_PREDICTION, RETRAIN_FLAG, MODEL, PREDICT_LABEL, DF_TRAIN
    try:
        DF_PREDICTION_PRE_PROCESS = preprocess_data_V2(DF_PREDICTION)
        PRED = PREDICT_LABEL
        lenght_pred = len(PRED)
        if lenght_pred > len(DF_PREDICTION_PRE_PROCESS.index):
            PRED = PREDICT_LABEL[:len(DF_PREDICTION_PRE_PROCESS.index)]
        if len(np.unique(PRED)) > 1:
            SCORE_PREDICTION = silhouette_score(DF_PREDICTION_PRE_PROCESS, PRED)
            print("Recoring of current model KMEANs: ", SCORE_PREDICTION)
            if SCORE_TRAIN - SCORE_PREDICTION <= 0.1:
                RETRAIN_FLAG = False
            if SCORE_TRAIN - SCORE_PREDICTION > 0.1:
                RETRAIN_FLAG = True
            if RETRAIN_FLAG:
                print("Retrain Occur")
                length_df_train = len(DF_TRAIN.index)
                length_df_predictions = len(DF_PREDICTION.index)
                if length_df_train <= length_df_predictions:
                    DF_TRAIN = DF_PREDICTION
                else:
                    DF_TRAIN = DF_TRAIN.iloc[length_df_predictions:]
                    DF_TRAIN = pd.concat([DF_TRAIN, DF_PREDICTION], ignore_index=True)
                threading.Thread(target=kmeans_model_train, kwargs={'df_raw': DF_TRAIN}).start()
                DF_PREDICTION = pd.DataFrame()
                PREDICT_LABEL = PREDICT_LABEL[len(DF_PREDICTION_PRE_PROCESS.index):]
                RETRAIN_FLAG = False
        else:
            pass      
    except Exception as e:
        print("Error training model: " + str(e))
        pass
        

def queue_message(message, dtypes):
    """
        Threading for message queue and throughput for prediction
    """
    message_decode = message.decode('utf8').replace("'", '"')
    log_data = reg_log_pattern.match(message_decode).groupdict()

    try:
        prometheus_url = f"http://{PROMETHEUS_HOSTNAME}:{PROMETHEUS_PORT}"
        query = '{__name__=~"node_network_receive_bytes_per_second|node_network_transmit_bytes_per_second"}'
        api_url = f'{prometheus_url}/api/v1/query?query={query}'
        response = requests.get(api_url, timeout=1)

        if response.status_code == 200:
            data = response.json()

            if 'data' in data and 'result' in data['data']:
                result = data['data']['result']
                if len(result) > 0:
                    network_receive_bytes_per_second = result[0]['value'][1]
                    network_transmit_bytes_per_second = result[1]['value'][1]
                else:
                    network_receive_bytes_per_second = 0
                    network_transmit_bytes_per_second = 0
            else:
                network_receive_bytes_per_second = 0
                network_transmit_bytes_per_second = 0
        else:
            network_receive_bytes_per_second = 0
            network_transmit_bytes_per_second = 0
    except Exception as e:
        network_receive_bytes_per_second = 0
        network_transmit_bytes_per_second = 0
        print("Error Request Occur: ", e)

    # Convert dataraw into dataframe format and predict
    format_log = list(log_data.values())
    format_log.append(network_receive_bytes_per_second)
    format_log.append(network_transmit_bytes_per_second)
    df_raw = initialize_input(format_log)
    if df_raw['upstream_response_time'].values[0] == "-":
        df_raw['upstream_response_time'] = 0
    df_raw = df_raw.astype(dtypes)
    while True:
        if MODEL_AVAILABLE == True:
            break
        if MODEL_AVAILABLE == False:
            continue
    kmeans_predict(df_raw)
    
def schedule_model():
    """Schedule the model for validation model, firewall decision
    """    
    schedule.every(30).minutes.do(validate_model)
    schedule.every(60).seconds.do(density_decision, amount_request=20)
    while True:
        schedule.run_pending()
        time.sleep(1)
        
def __main__():
    global DF_TRAIN, DF_PREDICTION, FIREWALL_FLAG, RETRAIN_FLAG
    global MODEL, SCORE_TRAIN, PREDICT_LABEL
    global NUMBER_OF_ATTACK_TRAIN, NUMBER_OF_NORMAL_TRAIN, NUMBER_OF_BENCHMARK_TRAIN
    global NUMBER_OF_ATTACK_PREDICT, NUMBER_OF_BENCHMARK_PREDICT, NUMBER_OF_NORMAL_PREDICT
    
    # Initialize the training model
    DF_TRAIN = pd.read_csv(PATH_TRAIN_DATA)
    DF_TRAIN_DTYPES = DF_TRAIN.dtypes.to_dict()
    threading.Thread(target=kmeans_model_train, args=(), kwargs={'df_raw': DF_TRAIN}).start()
    
    # Schedule for validation model, firewall handling
    threading.Thread(target=schedule_model).start()
    
    # Queue the message from kafka
    pool = ThreadPoolExecutor(max_workers=5)
    for message in consumer:
        try:
            pool.submit(queue_message, message.value, DF_TRAIN_DTYPES)
        except Exception as e:
            print("Error Queue Occur: ", e)

if __name__ == '__main__':
    try:
        __main__()
    except KeyboardInterrupt:
        print("End of queue and model AI")
        exit(1)
        
