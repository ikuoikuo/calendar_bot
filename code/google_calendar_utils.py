import datetime
import pytz
from googleapiclient.discovery import build
from google.auth import load_credentials_from_file

# 認証情報ファイルのパス
CREDENTIALS_PATH = '../credentials_service.json'
TOKEN_PATH = '../token.json'

# 認証範囲
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_schedule():
    creds = load_credentials_from_file(
      CREDENTIALS_PATH, SCOPES
    )[0]

    service = build('calendar', 'v3', credentials=creds)
    JST = pytz.timezone('Asia/Tokyo')
    # プログラム実行時間から1週間後までに期間を設定
    now = datetime.datetime.now(JST)
    start_time = now.isoformat()
    end_time = (now + datetime.timedelta(days=7)).isoformat() 

    events_result = service.events().list(calendarId='i.fujikawa0701@gmail.com', timeMin=start_time, timeMax=end_time,
                                          maxResults=50, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        return None
    
    schedule = []
    for event in events:
        event_info = {
            'summary': event.get('summary'),
            'start': event['start'].get('dateTime', event['start'].get('date')),
            'attendees': event.get('attendees', [])
        }
        schedule.append(event_info)
    return schedule

def count_workout_events(schedule):
    workout_count = {}
    for event in schedule:
        if 'ジム' in event['summary']:
            for attendee in event['attendees']:
                email = attendee.get('email')
                response_status = attendee.get('responseStatus')
                if email and response_status == 'accepted':
                    if email in workout_count:
                        workout_count[email] += 1
                    else:
                        workout_count[email] = 1
    return workout_count

if __name__ == '__main__':
    schedule = get_schedule()
    count = count_workout_events(schedule)
    print(count)
