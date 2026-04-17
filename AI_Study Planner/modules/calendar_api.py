from google_auth_oauthlib.flow import InstalledAppFlow          # For OAuth2 authentication with Google
from googleapiclient.discovery import build                     # To build Google Calendar API service
from config import SCOPES                                       # Import Google Calendar API scopes (permissions)
import datetime                                                 # For handling dates and times

# ---------------- AUTHENTICATE GOOGLE CALENDAR ----------------
def authenticate_google_calendar():
     # Load OAuth2 client secrets and start authentication flow
    flow = InstalledAppFlow.from_client_secrets_file(
        "credentials/client_secret.json",      # JSON file from Google Cloud Console
        SCOPES                                 # API permissions requested
    )

    credentials = flow.run_local_server(port=0)     # Open a browser for user login
    service = build('calendar', 'v3', credentials=credentials)  # Build the Calendar API service object
    return service  # Return service to interact with Google Calendar

# ---------------- GET EXISTING EVENTS ----------------
def get_existing_events(service):

    now = datetime.datetime.utcnow().isoformat() + "Z"   # Current time in UTC ISO format

    # Fetch next 10 events from primary calendar
    events_result = service.events().list(
        calendarId="primary",       # Only events starting after now
        timeMin=now,                
        maxResults=10,
        singleEvents=True,           # Expand recurring events
        orderBy="startTime"          # Sort by start time
    ).execute()

    return events_result.get("items", [])   # Return list of events

# ---------------- DELETE OLD AI STUDY EVENTS ----------------
def delete_old_events(service):
     # Fetch up to 100 existing events
    events = service.events().list(
        calendarId="primary",
        maxResults=100
    ).execute().get("items", [])

    for event in events:
        # Only delete events created by this AI Study Planner
        if "AI_STUDY_PLANNER" in event.get("description",""):

            service.events().delete(
                calendarId="primary",
                eventId=event["id"]
            ).execute()


# ---------------- ADD NEW EVENTS TO GOOGLE CALENDAR ----------------
def add_events_to_calendar(service, schedule):

    for _, row in schedule.iterrows():
         # Convert scheduled date and time strings into datetime object
        date_parts = list(map(int, row["Scheduled_Date"].split("-")))   # Split YYYY-MM-DD
        hour = int(row["Scheduled_Time"].split(":")[0])                 # Get hour part

        start = datetime.datetime(*date_parts, hour)    # Create start datetime
        end = start + datetime.timedelta(hours=2)       # End time 2 hours later

        # Color code: red for submission, green for normal tasks
        color = "11" if "Submit" in row["Task_Instruction"] else "5"

        # Event object to insert into calendar
        event = {
            "summary": row["Task_Instruction"], # Task title
            "description": f"AI_STUDY_PLANNER\nDue: {row['due_date']}", # Mark as AI Planner event
            "start": {"dateTime": start.isoformat(), "timeZone": "Asia/Kuala_Lumpur"},  # Start time
            "end": {"dateTime": end.isoformat(), "timeZone": "Asia/Kuala_Lumpur"},      # End time
            "colorId": color,    # Color code
            "reminders": {       # Pop-up reminder
            "useDefault": False,
            "overrides": [{"method": "popup", "minutes": 30}]
            }
        }
        # Insert event into primary calendar
        service.events().insert(calendarId="primary", body=event).execute()

    print("Events added successfully")  # Confirmation message
    