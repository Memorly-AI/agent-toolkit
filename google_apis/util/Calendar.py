from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_apis.util.Auth import Auth
from dateutil import parser 
import logging
import uuid

logger = logging.getLogger("django")

class Calendar(Auth):
    def __init__(self, user_id, apps=["calendar"]):
        super().__init__(user_id, apps=apps)
        self.service = None
        self.claender_uri = None

    def __enter__(self):
        creds = super().__enter__()
        if isinstance(creds, dict) and "auth_url" in creds:
            return creds

        self.service = build("calendar", "v3", credentials=creds)
        return self
    
    def create_google_calendar_event(self, summary, start_time, end_time, attendees, description=""):
        """
        Create a primary calendar event with a generated Google Meet link.
        Automatically fixes date formats to RFC3339 (adds seconds if missing).
        """
        try:
            dt_start = parser.parse(start_time)
            dt_end = parser.parse(end_time)
            fmt_start = dt_start.isoformat()
            fmt_end = dt_end.isoformat()

            event_body = {
                "summary": summary,
                "description": description,
                "start": {
                    "dateTime": fmt_start,
                    "timeZone": "Asia/Kolkata"
                },
                "end": {
                    "dateTime": fmt_end,
                    "timeZone": "Asia/Kolkata"
                },
                # List comprehension filters out empty emails to prevent 400 errors
                "attendees": [{"email": email} for email in attendees if email],
                "conferenceData": {
                    "createRequest": {
                        "requestId": f"memorly-{uuid.uuid4()}",
                        "conferenceSolutionKey": {"type": "hangoutsMeet"}
                    }
                }
            }
            
            event = self.service.events().insert(
                calendarId="primary",
                body=event_body,
                conferenceDataVersion=1,
                sendUpdates="all"
            ).execute()

            return {
                "event_id": event["id"],
                "meet_link": event.get("hangoutLink"),
                "status": "success"
            }

        except HttpError as e:
            error_content = e.content.decode('utf-8')
            logger.error(f"Google Calendar API Error: {error_content}")
            return {
                "status": "error", 
                "message": "Google API Error", 
                "details": error_content
            }
            
        except Exception as e:
            logger.exception("Unexpected error in create_google_calendar_event")
            return {"status": "error", "message": str(e)}
        