from google_calendar_utils import get_schedule, count_workout_events

def main():
    schedule = get_schedule()
    count = count_workout_events(schedule)
    print(count)

if __name__ == '__main__':
    main()
