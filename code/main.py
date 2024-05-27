from google_calendar_utils import get_schedule, count_workout_events
import requests
import json

members_file_path = '../data/group_members.json'

def call_send_message(message_text):
    url = 'http://localhost:8080/send_message'
    params = {'message': message_text}
    try:
        response = requests.get(url, params=params)
        print(f'Status Code: {response.status_code}')
        print(f'Response Body: {response.text}')
    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')
        
def generate_message(name,workout_count):
    if workout_count == 0:
        return f"@{name}\n来週1週間筋トレの予定ないのやばいよ。\n焦った方がいいよ。"
    elif workout_count == 1 or workout_count == 2:
        return f"@{name}\n週3KPI達成しろって。\n来週{workout_count}回じゃ甘いって。"
    else:
        return None

def main():
    schedule = get_schedule()
    count = count_workout_events(schedule)
    print(count)
    with open(members_file_path, 'r', encoding='utf-8') as file:
        name_data = json.load(file)
    for email, count in count.items():
        message = generate_message(name_data[email],count)
        if message:
            call_send_message(message)

if __name__ == '__main__':
    main()
