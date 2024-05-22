from flask import Flask, request, abort
from linebot import WebhookHandler, LineBotApi
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, JoinEvent
from dotenv import load_dotenv
import os
import csv

app = Flask(__name__)

# 環境変数をロード
load_dotenv()
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')
CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')

if not CHANNEL_SECRET or not CHANNEL_ACCESS_TOKEN:
    raise ValueError("CHANNEL_SECRET and CHANNEL_ACCESS_TOKEN must be set in environment variables.")

handler = WebhookHandler(CHANNEL_SECRET)
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 相手の送信した内容で条件分岐して回答を変数に代入
    if event.message.text == 'グー':
        reply_message = 'パー'
    elif event.message.text == 'チョキ':
        reply_message = 'グー'
    elif event.message.text == 'パー':
        reply_message = 'チョキ'
    else:
        reply_message = 'ごめんね。\nまだ他のメッセージには対応してないよ'

    # メッセージを返信
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
