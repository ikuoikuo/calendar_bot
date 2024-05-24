import os.path
import datetime
import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 認証情報ファイルのパス
CREDENTIALS_PATH = '../credentials.json'
TOKEN_PATH = '../token.json'

# 認証範囲
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_schedule():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=64619)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    JST = pytz.timezone('Asia/Tokyo')
    # プログラム実行時間から1週間後までに期間を設定
    now = datetime.datetime.now(JST)
    start_time = now.isoformat()
    end_time = (now + datetime.timedelta(days=7)).isoformat() 

    events_result = service.events().list(calendarId='primary', timeMin=start_time, timeMax=end_time,
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
                if email:
                    if email in workout_count:
                        workout_count[email] += 1
                    else:
                        workout_count[email] = 1
    return workout_count

if __name__ == '__main__':
    schedule = get_schedule()
    count = count_workout_events(schedule)
    print(count)
