from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_apis.util.Auth import Auth


class Meet(Auth):

    def __init__(self, scopes=None):
        super().__init__(scopes)
        self.service = None
        self.meeting_uri = None

    def __enter__(self):
        creds = super().__enter__()
        if isinstance(creds, dict) and "auth_url" in creds:
            return creds

        self.service = build("calendar", "v3", credentials=creds)
        return self

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

