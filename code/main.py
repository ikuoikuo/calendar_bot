from google_calendar_utils import get_schedule, count_workout_events

def generate_message(workout_count):
    if workout_count == 0:
        return "来週1週間筋トレの予定ないのやばいよ。\n焦った方がいいよ。"
    elif workout_count == 1 or workout_count == 2:
        return "週3KPI達成しろって。甘いって。"
    else:
        return None

def main():
    schedule = get_schedule()
    count = count_workout_events(schedule)
    print(count)

if __name__ == '__main__':
    main()
