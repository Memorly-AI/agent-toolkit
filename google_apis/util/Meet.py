from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_apis.util.Auth import Auth
import logging
from datetime import datetime, timedelta


logger = logging.getLogger("django")


class Meet(Auth):
    def __init__(self, user_id, apps=["meet"]):
        super().__init__(user_id, apps=apps)
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
            return self.meeting_uri
        except HttpError as error:
            return error
    

    def find_event_by_meeting_link(self, meeting_code, start_time=None, end_time=None):
        """Find an event by the Google Meet code and optional time range"""
        try:
            if "meet.google.com/" in meeting_code:
                meeting_code = meeting_code.split("meet.google.com/")[1]
            
            if not start_time:
                now = datetime.utcnow()
                time_min = now - timedelta(days=30)
                time_max = now + timedelta(days=60)
            else:
                if 'Z' in start_time:
                    start_time = start_time.replace('Z', '+00:00')
                elif not '+' in start_time and not '-' in start_time[-6:]:
                    start_time = start_time + '+00:00'
                    
                dt_start = datetime.fromisoformat(start_time)
                time_min = dt_start - timedelta(days=1)
                
                if end_time:
                    if 'Z' in end_time:
                        end_time = end_time.replace('Z', '+00:00')
                    elif not '+' in end_time and not '-' in end_time[-6:]:
                        end_time = end_time + '+00:00'
                        
                    dt_end = datetime.fromisoformat(end_time)
                    time_max = dt_end + timedelta(days=1)
                else:
                    time_max = dt_start + timedelta(days=3)
            
            time_min_str = time_min.isoformat().replace('+00:00', 'Z')
            time_max_str = time_max.isoformat().replace('+00:00', 'Z')
            
            events = self.service.events().list(
                calendarId="primary",
                timeMin=time_min_str,
                timeMax=time_max_str,
                singleEvents=True,
                maxResults=100
            ).execute()
            
            for event in events.get('items', []):
                conference_data = event.get('conferenceData', {})
                entry_points = conference_data.get('entryPoints', [])
                
                for entry in entry_points:
                    uri = entry.get('uri', '')
                    if meeting_code in uri:
                        return event['id'] 
                        
            return None  
        except Exception as error:
            logger.error(f"Error finding event: {error}")
            return None
    

    def update_by_meeting_link(self, meeting_link, summary, start_time, end_time, timezone):
        """Update a meeting by finding its event ID first using the meeting link"""
        try:
            event_id = self.find_event_by_meeting_link(meeting_link, start_time, end_time)
            
            if not event_id:
                return {"error": f"Meeting with link {meeting_link} not found in calendar"}
                
            return self.update(event_id, summary, start_time, end_time, timezone)
        except Exception as error:
            logger.error(f"Error in update_by_meeting_link: {error}")
            return {"error": str(error)}
        

    def update(self, meet_id, summary, start_time, end_time, timezone):
        try:
            try:
                existing_event = self.service.events().get(
                    calendarId="primary", 
                    eventId=meet_id
                ).execute()
            except HttpError as get_error:
                if get_error.resp.status == 404:
                    logger.error(f"Event ID {meet_id} not found in calendar")
                return get_error
            
            conference_data = existing_event.get('conferenceData', {})
            event = {
                "summary": summary,
                "start": {"dateTime": start_time, "timeZone": timezone},
                "end": {"dateTime": end_time, "timeZone": timezone},
                "conferenceData": conference_data  
            }
            
            event = (
                self.service.events()
                .update(calendarId="primary", eventId=meet_id, body=event, conferenceDataVersion=1)
                .execute()
            )
            self.meeting_uri = event.get("hangoutLink")
            return self.meeting_uri
        except HttpError as error:
            print(f"Error updating event: {error}")
            return error
        

    def get_all_meetings(self):
        try:
            events = self.service.events().list(calendarId="primary").execute()
            return events.get("items", [])
        except HttpError as error:
            return error
        
    
    def get_meeting_by_id(self, meet_id):
        try:
            event = self.service.events().get(calendarId="primary", eventId=meet_id).execute()
            return event
        except HttpError as error:
            return error
        

    def get_meeting_by_link(self, meeting_link):
        try:
            meeting_code = meeting_link
            if "meet.google.com/" in meeting_link:
                meeting_code = meeting_link.split("meet.google.com/")[1].split("?")[0]
            
            time_min = (datetime.utcnow() - timedelta(days=30)).isoformat() + 'Z'
            time_max = (datetime.utcnow() + timedelta(days=365)).isoformat() + 'Z'
            
            # Get events with pagination handling
            page_token = None
            while True:
                events_result = self.service.events().list(
                    calendarId="primary",
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=100,
                    singleEvents=True,
                    orderBy='startTime',
                    pageToken=page_token
                ).execute()
                
                # Search through events on this page
                for event in events_result.get("items", []):
                    # Check hangoutLink for exact match
                    if event.get("hangoutLink") == meeting_link:
                        return event
                    
                    # Also check for meeting code match (more flexible)
                    hangout_link = event.get("hangoutLink", "")
                    if meeting_code in hangout_link:
                        return event
                    
                    # Check conferenceData as well
                    conf_data = event.get("conferenceData", {})
                    entry_points = conf_data.get("entryPoints", [])
                    for entry in entry_points:
                        uri = entry.get("uri", "")
                        if meeting_code in uri:
                            return event
                
                # Get the next page of events, if any
                page_token = events_result.get('nextPageToken')
                if not page_token:
                    break
                    
            # No matching event found
            return None
        except HttpError as error:
            print(f"Error getting meeting by link: {error}")
            return error


    def get_meeting_by_date(self, start_date, end_date):
        try:
            if not start_date.endswith('Z') and 'T' in start_date:
                start_date = start_date + 'Z'
            if not end_date.endswith('Z') and 'T' in end_date:
                end_date = end_date + 'Z'
                
            events = self.service.events().list(
                calendarId="primary", 
                timeMin=start_date, 
                timeMax=end_date,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events.get("items", [])
        except HttpError as error:
            print(f"Error details: {error}")
            return error
    
        
    def delete(self, meet_id):
        try:
            self.service.events().delete(calendarId="primary", eventId=meet_id).execute()
            return True
        except HttpError as error:
            return error
        

    def delete_by_meeting_link(self, meeting_link):
        """Delete a meeting using its Google Meet link"""
        try:
            event = self.get_meeting_by_link(meeting_link)

            if not event:
                return {"error": f"Meeting with link {meeting_link} not found in calendar"}

            event_id = event.get("id")
            result = self.delete(event_id)
            if result is True:
                return {"success": True, "message": f"Meeting with link {meeting_link} successfully deleted"}
            else:
                return result    
        except Exception as error:
            print(f"Error in delete_by_meeting_link: {error}")
            return {"error": str(error)}


    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

