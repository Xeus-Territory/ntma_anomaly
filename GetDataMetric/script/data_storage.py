import json 
import redis
from kafka import KafkaConsumer

if __name__ == '__main__':
    # Redis
    r = redis.Redis(host='192.168.127.128', port=6379, db=0)

    # Init pipeline
    pipe = r.pipeline()

    # Kafka Consumer 
    consumer = KafkaConsumer(
        'prometheus-metrics',
        bootstrap_servers='192.168.127.128:9092',
        auto_offset_reset='earliest'
    )

    timestamp = "2023-05-11T09:37:37Z"

    for message in consumer:
        my_bytes_value = message.value
        my_json = my_bytes_value.decode('utf8').replace("'", '"')

        try:
            data = json.loads(my_json)

            if (timestamp != data['timestamp']):
                pipe.expire(timestamp, 3600)
                pipe.execute()
                timestamp = data['timestamp']
                pipe.hsetnx(data['timestamp'], data['name'], data['value'])
            else:
                pipe.hsetnx(data['timestamp'], data['name'], data['value'])

        except:
            pass
