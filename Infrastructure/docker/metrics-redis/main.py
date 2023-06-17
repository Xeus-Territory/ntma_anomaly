import requests
import schedule
import logging
import time
import json
import re
import os

from kafka import KafkaConsumer
from concurrent.futures import ThreadPoolExecutor
from redis import Redis
from redis.connection import ConnectionPool
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

PROMETHEUS_HOSTNAME = os.getenv('PROMETHEUS_HOSTNAME')
PROMETHEUS_PORT = os.getenv('PROMETHEUS_PORT')
REDIS_HOSTNAME = os.getenv('REDIS_HOSTNAME')
REDIS_PORT = os.getenv('REDIS_PORT')
KAFKA_HOSTNAME = os.getenv('KAFKA_HOSTNAME')
KAFKA_PORT = os.getenv('KAFKA_PORT')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')

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

# Create global variables
network_receive_bytes_per_second = 0
network_transmit_bytes_per_second = 0

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

    def add_log_to_redis(self, key, log_data):
        try:
            self.connection.lpush(key, json.dumps(log_data))
            self.connection.expire(key, 259200)
            logging.info(f"Data added successfully with key '{key}'")
        except Exception as e:
            logging.error(f"Error processing message: {e}")


def get_metrics():
    global network_receive_bytes_per_second
    global network_transmit_bytes_per_second

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
        logging.error(f"Error processing message: {e}\n------\n")


def process_message(message):
    try:
        time_format = "%d/%b/%Y:%H:%M:%S %z"
        my_bytes_value = message.value
        my_json = my_bytes_value.decode('utf8').replace("'", '"')
        log_data = reg_log_pattern.match(my_json).groupdict()

        key = datetime.strptime(log_data['time_local'], time_format).strftime("%Y-%m-%d-%H")

        log_data["network_receive_bytes_per_second"] = network_receive_bytes_per_second
        log_data["network_transmit_bytes_per_second"] = network_transmit_bytes_per_second

        redis_connection.add_log_to_redis(key, log_data)

    except Exception as e:
        logging.error(f"Error processing message: {e}\n------\n=> Message: {my_json}\n------\n")


def run_scheduler():
    schedule.every(1).seconds.do(get_metrics)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    # Kafka Consumer
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=f"{KAFKA_HOSTNAME}:{KAFKA_PORT}",
        auto_offset_reset='latest',
        max_poll_records=1000
    )

    redis_connection = RedisConnection()

    executor = ThreadPoolExecutor(max_workers=5)
    executor.submit(run_scheduler)

    while True:
        batch = consumer.poll(timeout_ms=200)
        for topic_partition, records in batch.items():
            for record in records:
                executor.submit(process_message, record)
