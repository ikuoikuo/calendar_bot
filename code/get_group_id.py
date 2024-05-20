from flask import Flask, request, abort
import requests
import json
from dotenv import load_dotenv
import os
import csv

app = Flask(__name__)

env = load_dotenv()
ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')

HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}

URL = 'https://api.line.me/v2/bot/message/push'

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        print("-----------------------------")
        body = request.get_json()
        events = body.get('events', [])
        
        for event in events:
            if event['type'] == 'message':
                group_id = event['source'].get('groupId')
                message = event['message']['text']
                
                send_message(group_id, f"Received message: {message}")
            
            elif event['type'] == 'join':
                group_id = event['source'].get('groupId')
                add_group_id_to_csv(group_id)
                if group_id:
                    send_message(group_id, "厳しいって")
        return 200
    else:
        abort(400)

def add_group_id_to_csv(group_id):
    csv_file_path = '../data/group_id.csv'
    
    file_exists = os.path.isfile(csv_file_path)
    
    with open(csv_file_path, mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        if not file_exists:
            writer.writerow(['group_id'])
        writer.writerow([group_id])
    return 

def send_message(to, text):
    data = {
        "to": to,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }
    
    response = requests.post(URL, headers=HEADERS, data=json.dumps(data))
    if response.status_code != 200:
        print(f"エラー: {response.status_code}")
        print(response.text)
    return 

if __name__ == '__main__':
    app.run(port=5000)
