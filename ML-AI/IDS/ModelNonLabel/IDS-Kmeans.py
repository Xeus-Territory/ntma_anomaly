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
import json
from kafka import KafkaConsumer

# Load the environment variable
load_dotenv()
IP_MANAGER = os.environ.get('IP_MANAGER')
OPENPORT = os.environ.get('OPENPORT')

## Initialize the param for training 
PATH_TRAIN_DATA = '../../Data/Collection/data_raw.csv'
PATH_RESULT = '../../Data/Collection/result_kmeans.csv'
FIREWALL_FLAG = False
RETRAIN_FLAG = False
MODEL = KMeans()
SCORE_TRAIN = 0
DF_TRAIN = pd.DataFrame()
DF_PREDICTION = pd.DataFrame()
PREDICT_LABEL = []
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
        DF_TRAIN = pd.DataFrame(columns=template_columns)
    if type == 'predict':
        path = PATH_RESULT
        template_columns = list(pd.read_csv(path).columns)
        DF_PREDICTION = pd.DataFrame(columns=list(template_columns))  
        
def density_decision(number_req_normal, number_req_abnormal):
    global FIREWALL_FLAG
    total = number_req_normal + number_req_abnormal
    if total >= 1000:
        # Idea: if the number of normal requests have density >= 80 % (NORMAL)
        #       if the number of normal requests have density < 80 % (ABNORMAL)
        density = (number_req_normal / total)
        if density >= 0.8:
            if FIREWALL_FLAG == True:
                FIREWALL_FLAG = False
                requests.post('http://'+ str(IP_MANAGER) + ":" + str(OPENPORT) + "/firewall?state=down")
        else:
            if FIREWALL_FLAG == False:
                FIREWALL_FLAG = True
                requests.post('http://'+ str(IP_MANAGER) + ":" + str(OPENPORT) + "/firewall?state=up")             
    else:
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
    method = df['request_method'].values[0]
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
    version = df['http_version'].values[0]
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
    
    return df

def post_processing(df_predict):
    """Post Processing of data after prediction about assign label and fix actually right situations

    Args:
        df_predict (dataframe): dataframe after prediction by model and assigned label by model AI

    Returns:
        dataframe: new dataframe after post-processiong and fix correction situation
    """   
    df = df_predict
    # Change label base on the assign number
    df.loc[(df['cluster_kmeans'] == 1), ['cluster_kmeans']] = "normal"
    df.loc[(df['cluster_kmeans'] == 3), ['cluster_kmeans']] = "webattack"
    df.loc[(df['cluster_kmeans'] == 2), ['cluster_kmeans']] = "benchmark"
    
    # Change label cluster info base on the knowledge
    df.loc[(df['request_time'] <= 0.2) & (df['network_receive_bytes_per_second'] <= 1900000), ['cluster_kmeans']] = "normal"
    df.loc[((df['request_time'] > 0.2) & (df['network_receive_bytes_per_second'] <= 3500000)) | ((df['network_receive_bytes_per_second'] > 1900000) & (df['network_receive_bytes_per_second'] <= 3500000)), ['cluster_kmeans']] = "webattack"
    df.loc[(df['network_receive_bytes_per_second'] > 3500000), ['cluster_kmeans']] = "benchmark"
    
    # Fix the situation need to right
    df.loc[(df['valid_user_agent'] == 1) & (df['available_request'] == 1), ['cluster_kmeans']] = "normal"
    
    return df

def kmeans_model_train(df_raw):
    """Building a kmeans for trainning process

    Args:
        df_preprocess (_type_): _description_
        
    """ 
    global MODEL, SCORE_TRAIN, NUMBER_OF_NORMAL_TRAIN, NUMBER_OF_ATTACK_TRAIN, NUMBER_OF_BENCHMARK_TRAIN   
    df = preprocess_data(df_raw)
    
    # KMeans
    kmean3 = KMeans(n_clusters=3)
    kmean3.fit(df)
    silhouette_score_average = silhouette_score(df, kmean3.predict(df))
    MODEL = kmean3
    SCORE_TRAIN = silhouette_score_average
    
    y_pred = MODEL.fit_predict(df)
    df['cluster_kmeans'] = y_pred+1
    
    # Post-process for dataframe
    df = post_processing(df)
    
    # Statictis the label
    NUMBER_OF_NORMAL_TRAIN = df['cluster_kmeans'].value_counts()['normal']
    NUMBER_OF_ATTACK_TRAIN = df['cluster_kmeans'].value_counts()['webattack']
    NUMBER_OF_BENCHMARK_TRAIN = df['cluster_kmeans'].value_counts()['benchmark']

def kmeans_predict(df_raw):
    """Prediction for each log through by message queue from kafka

    Args:
        df_raw (dataframe): Raw data pass for prediction proccess from kafka 
    """    
    global NUMBER_OF_NORMAL_PREDICT, NUMBER_OF_BENCHMARK_PREDICT, NUMBER_OF_ATTACK_PREDICT, DF_TRAIN, MODEL
    DF_PREDICTION = pd.concat([DF_PREDICTION, df_raw], ignore_index= True)
    df = preprocess_data_V2(df_raw)
    y_pred = MODEL.predict(df)
    df['cluster_kmeans'] = y_pred+1
    df = post_processing(df)
    state_req = df['cluster_kmeans'].values[0]
    print(state_req)
    if state_req == "normal":
        PREDICT_LABEL.append(1)
        NUMBER_OF_NORMAL_PREDICT = NUMBER_OF_NORMAL_PREDICT + 1
    if state_req == "webattack":
        PREDICT_LABEL.append(3)
        NUMBER_OF_ATTACK_PREDICT = NUMBER_OF_ATTACK_PREDICT + 1
    if state_req == "benchmark":
        PREDICT_LABEL.append(2)
        NUMBER_OF_BENCHMARK_PREDICT = NUMBER_OF_BENCHMARK_PREDICT + 1
        
def validate_model():
    """
        Validate the model base on silhouette score for give evaluation for curren model
    """    
    global SCORE_TRAIN, DF_TRAIN, DF_PREDICTION, PREDICT_LABEL, RETRAIN_FLAG
    SCORE_PREDICTION = silhouette_score(DF_TRAIN, PREDICT_LABEL)
    if SCORE_TRAIN - SCORE_PREDICTION <= 0.1:
        RETRAIN_FLAG = False
    if SCORE_TRAIN - SCORE_PREDICTION > 0.1:
        RETRAIN_FLAG = True
    if RETRAIN_FLAG:
        length_df_train = len(DF_TRAIN.index)
        length_df_predictions = len(DF_PREDICTION.index)
        if length_df_train <= length_df_predictions:
            DF_TRAIN = DF_PREDICTION
        else:
            DF_TRAIN = DF_TRAIN.iloc[length_df_predictions:]
            DF_TRAIN = pd.concat([DF_TRAIN, DF_PREDICTION], ignore_index=True)
        kmeans_model_train(DF_TRAIN)
        RETRAIN_FLAG = False
        
        
def __main__():
    pass    

consumer = KafkaConsumer(
    "log",
    bootstrap_servers="192.168.66.1:9092",
    auto_offset_reset='earliest'
)

for message in consumer:
    my_bytes_value = message.value
    # my_json = my_bytes_value.decode('utf8').replace("'", '"')
    print(my_bytes_value)

    
    
    
    
    