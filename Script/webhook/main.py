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

@app.route('/alerts', methods=['POST'])
def alerts():
    data = request.json
    data = data["alerts"][0]
    
    # Your analysis and processing here!
    print("Scaling ....")

    # Send alert to telegram
    send_test_message(data)
    return 'OK'

def send_test_message(data):
    try:
        # print(data)
        message = "=========🔥 Alert 🔥======== " \
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

if __name__ == '__main__':
    app.run(host="0.0.0.0")