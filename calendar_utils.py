from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


# Define the scope for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_PATH = 'token.json'  # Already generated during auth
CALENDAR_ID = 'primary'    # Using your main calendar
# to authenticate and return calendar service
def get_calendar_service():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    service = build('calendar', 'v3', credentials=creds)
    return service

#  To find available time slots on a specific day
def get_free_slots(date: str, duration: int):
    service = get_calendar_service()

    start_day = datetime.fromisoformat(date + 'T00:00:00')
    end_day = datetime.fromisoformat(date + 'T23:59:59')

    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start_day.isoformat() + 'Z',
        timeMax=end_day.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    free_slots = []
    current_time = start_day

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        event_start = datetime.fromisoformat(start)
        event_end = datetime.fromisoformat(end)

        gap = (event_start - current_time).total_seconds() / 60
        if gap >= duration:
            free_slots.append({
                "start": current_time.isoformat(),
                "end": event_start.isoformat()
            })
        current_time = max(current_time, event_end)

    if (end_day - current_time).total_seconds() / 60 >= duration:
        free_slots.append({
            "start": current_time.isoformat(),
            "end": end_day.isoformat()
        })

    return free_slots

# Step 3: Book an event
def create_event(summary, description, start, end):
    service = get_calendar_service()

    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start,
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end,
            'timeZone': 'Asia/Kolkata',
        },
    }

    created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return created_event
from fastapi import HTTPException

def get_free_slots(date: str, duration: int):
    try:
        start_day = datetime.fromisoformat(date + 'T00:00:00')
        end_day = datetime.fromisoformat(date + 'T23:59:59')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Expected YYYY-MM-DD.")
    
