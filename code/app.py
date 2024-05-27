from flask import Flask, request, abort, jsonify
from linebot import WebhookHandler, LineBotApi
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, JoinEvent
from dotenv import load_dotenv
import requests
import os
import csv

app = Flask(__name__)

load_dotenv()
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')
CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')

if not CHANNEL_SECRET or not CHANNEL_ACCESS_TOKEN:
    raise ValueError("CHANNEL_SECRET and CHANNEL_ACCESS_TOKEN must be set in environment variables.")

handler = WebhookHandler(CHANNEL_SECRET)
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

def load_group_ids(file_path):
    """ ファイルからグループIDを読み込む """
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

def send_push_message(token, user_id, message_text):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    data = {
        'to': user_id,
        'messages': [{
            'type': 'text',
            'text': message_text
        }]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code, response.text

@app.route("/send_message")
def send_message():
    token =  os.getenv('CHANNEL_ACCESS_TOKEN') 
    user_ids = load_group_ids('../data/group_id.csv')
    message_text = request.args.get('message', 'こんにちは、これはプッシュメッセージです！') 
    results = []
    for user_id in user_ids:
        status_code, response_text = send_push_message(token, user_id, message_text)
        results.append({'user_id': user_id, 'Status Code': status_code, 'Response': response_text})
    return jsonify(results)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == 'グー':
        reply_message = 'パー'
    elif event.message.text == 'チョキ':
        reply_message = 'グー'
    elif event.message.text == 'パー':
        reply_message = 'チョキ'
    else:
        reply_message = 'ごめんね。\nまだ他のメッセージには対応してないよ'

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )

@handler.add(JoinEvent)
def handle_join(event):
    group_id = event.source.group_id
    add_group_id_to_csv(group_id)
    line_bot_api.push_message(group_id, TextSendMessage(text="厳しいって"))

def add_group_id_to_csv(group_id):
    csv_file_path = '../data/group_id.csv'
    file_exists = os.path.isfile(csv_file_path)
    
    with open(csv_file_path, mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        if not file_exists:
            writer.writerow(['group_id'])
        writer.writerow([group_id])
    return 

if __name__ == '__main__':
    app.run(port=8080)
