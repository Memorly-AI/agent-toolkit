import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from utils.constants import get_env_variable


class Meet:
    def __init__(self, scopes=None):
        self.meeting_uri = None
        self.credentials = get_env_variable("GOOGLE_API_CREDENTIALS_PATH")
        if scopes is not None:
            self.SCOPES = scopes
        else:
            self.SCOPES = ["https://www.googleapis.com/auth/calendar"]

    def __enter__(self):
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open("token.json", "w") as token:
                token.write(creds.to_json())
        try:
            self.service = build("calendar", "v3", credentials=creds)
            return self
        except Exception as error:
            print(f"An error occurred: {error}")
            return error

    def create(self, summary, start_time, end_time, timezone):
        event = {
            "summary": summary,
            "start": {"dateTime": start_time, "timeZone": timezone},
            "end": {"dateTime": end_time, "timeZone": timezone},
            "conferenceData": {"createRequest": {"requestId": "sample123"}},
        }
        try:
            event = (
                self.service.events()
                .insert(calendarId="primary", body=event, conferenceDataVersion=1)
                .execute()
            )
            self.meeting_uri = event.get("hangoutLink")
            print(f"Meet link created: {self.meeting_uri}")
            return self.meeting_uri
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

