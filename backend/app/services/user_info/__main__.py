import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class UserInfo:
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
        return build('oauth2', 'v2', credentials=self.credentials)

    def get_email(self):
        user_info = self.service.userinfo().get().execute()
        return user_info['email']
