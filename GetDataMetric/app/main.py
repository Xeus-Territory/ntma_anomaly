import os
import json 
import redis
from kafka import KafkaConsumer
from dotenv import load_dotenv

load_dotenv()

REDIS_HOSTNAME = os.getenv('REDIS_HOSTNAME')
REDIS_PORT = os.getenv('REDIS_PORT')
KAFKA_HOSTNAME = os.getenv('KAFKA_HOSTNAME')
KAFKA_PORT = os.getenv('KAFKA_PORT')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')

if __name__ == '__main__':
    # Redis
    r = redis.Redis(host=REDIS_HOSTNAME, port=REDIS_PORT, db=0)    

    # Init pipeline
    pipe = r.pipeline()

    # Kafka Consumer 
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=f"{KAFKA_HOSTNAME}:{KAFKA_PORT}",
        auto_offset_reset='earliest'
    )
    count = 0
    timestamp = "2023-05-11T09:37:37Z"

    for message in consumer:
        my_bytes_value = message.value
        my_json = my_bytes_value.decode('utf8').replace("'", '"')
        count = count + 1
        try:
            data = json.loads(my_json)
            # print(data)
            # print(count, data['labels']['name'], "\t\t\t\t", data['value'])
            if (timestamp != data['timestamp']):
                pipe.expire(timestamp, 259200)
                print(pipe.execute())
                timestamp = data['timestamp']
                pipe.hsetnx(data['timestamp'], data['name'], data['value'])
            else:
                pipe.hsetnx(data['timestamp'], data['name'], data['value'])
            # r.hsetnx(data['timestamp'], data['name'], data['value'])
            # print(count, "OK!")
            # print(count, data['name'], data['value'], data['timestamp'])
        except Exception as e:
            print(f"Error processing message {count}: {e}")
            # print(count, my_json)
            # pass