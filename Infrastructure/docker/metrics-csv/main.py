import schedule
import logging
import redis
import json
import time
import csv
import os

from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

REDIS_HOSTNAME = os.getenv('REDIS_HOSTNAME')
REDIS_PORT = os.getenv('REDIS_PORT')

# Connect redis-server
r = redis.Redis(host=REDIS_HOSTNAME, port=REDIS_PORT, db=0)

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

def job():
    current_time = datetime.now()
    key = (current_time - timedelta(hours=1)).strftime("%Y-%m-%d-%H")

    if r.exists(key):
        data_list = r.lrange(key, 0, -1)
        parsed_data_list = [json.loads(data) for data in data_list[::-1]]

        parent_folder = "/log_data"
        os.makedirs(parent_folder, exist_ok=True)
        
        folder_name = current_time.strftime("%Y-%m-%d")
        folder_path = os.path.join(parent_folder, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        csv_file = os.path.join(folder_path, f"{key}.csv")

        # To check if a CSV file does not exist
        if not os.path.isfile(csv_file):
            with open(csv_file, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=parsed_data_list[0].keys())
                writer.writeheader()
                writer.writerows(parsed_data_list)

            logging.info(f"The data has been written to the '{csv_file}' file.")
        else:
            logging.info(f"The '{csv_file}' file already exists.")
    else:
        logging.info("Key does not exist in Redis")

schedule.every().hours.at(":01").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)