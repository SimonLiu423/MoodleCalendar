import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Wrap google calendar api
class GoogleCalendar:
    def __init__(self, credentials_path, token_path):
        self.scopes = [
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/calendar',
        ]
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.credentials = self.get_credentials(credentials_path, token_path)
        self.service = self.build_service()
        self.timezone = 'Asia/Taipei'

    def get_credentials(self, credentials_path, token_path):
        creds = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.scopes)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        return creds

    def build_service(self):
        return build('calendar', 'v3', credentials=self.credentials)

    # list calendars
    def list_calendars(self):
        calendars = self.service.calendarList().list().execute()
        return calendars.get('items', [])

    # create calendar
    def create_calendar(self, summary, description):
        calendar = {
            'summary': summary,
            'description': description,
            'timeZone': self.timezone,
        }
        calendar = self.service.calendars().insert(body=calendar).execute()
        return calendar.get('id')

    def create_event(self, calendar_id, title, start_time, end_time, description, color_id=1):
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': self.timezone
            },
            'end': {
                'dateTime': end_time,
                'timeZone': self.timezone
            },
            'colorId': str(color_id),
        }
        event = self.service.events().insert(calendarId=calendar_id, body=event).execute()
        return event.get('htmlLink')

    def update_event(
            self, calendar_id, event_id, title, start_time, end_time, description, color_id=1):
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': self.timezone,
            },
            'end': {
                'dateTime': end_time,
                'timeZone': self.timezone,
            },
            'colorId': str(color_id),
        }
        event = self.service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
        return event.get('htmlLink')

    def delete_event(self, calendar_id, event_id):
        self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

    # list events of a calendar in a time range
    def list_events(self, calendar_id, time_min, time_max):
        events = self.service.events().list(calendarId=calendar_id, timeMin=time_min, timeMax=time_max).execute()
        return events.get('items', [])

    def get_colors(self):
        colors = self.service.colors().get().execute()
        return colors
