from flask import Flask, request
from dotenv import load_dotenv
import os
import telebot

# Get environment variable 
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID   = os.getenv('CHAT_ID')

bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

def send_test_message(data):
    """Generates a Message object and sends it to the telegram by bot

    Args:
        data (dict): data get from the resquest json
    """    
    try:
        # print(data)
        message = "=========🔥 Alert 🔥========= " \
        + "\nStatus: "          + data["status"] \
        + "\n\nLabels:" \
        + "\n  → Alertname: "   + data["labels"]["alertname"] \
        + "\n  → Instance: "    + data["labels"]["instance"] \
        + "\n  → Severity: "    + data["labels"]["severity"] \
        + "\n\nAnnotations:" \
        + "\n  → Description: " + data["annotations"]["description"] \
        + "\n  → Summary: "     + data["annotations"]["summary"] \
        + "\n\nStarts at: "     + data["startsAt"] \
        + "\nEnds at: "         + data["endsAt"] \
        + "\n================= \n"

        bot.send_message(CHAT_ID, message)
    except Exception as ex:
        print(ex)

def scaling_job(name_service, action):
    """Scaling job for a given

    Args:
        name_service (string): which container of service meet trouble and need to scale
        action (string): string with scaling (UP or DOWN)

    """    
    print("Scaling " + action + "...")
    os.system('./scale-service-swarm.sh ' + name_service + ' ' + action)

@app.route('/alerts', methods=['POST'])
def alerts():
    data = request.json
    data = data["alerts"][0]
    
    # Your analysis and processing here!
    print(request.json['alerts'][0]['labels']['name'])
    scaling_job(request.json['alerts'][0]['labels']['name'], "up")

    # Send alert to telegram
    send_test_message(data)
    return 'OK'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000")