import os.path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import os
from email.message import EmailMessage
import mimetypes
import requests
from utils.constants import get_env_variable
from google_apis.util.Auth import Auth
import email
import copy
from email.utils import parsedate_to_datetime
from datetime import datetime
import json
import logging

logger = logging.getLogger('django')


class Gmail(Auth):

    def __init__(self, user_id, apps=["gmail"]):
        super().__init__(user_id, apps)
        self.gmail = None
        self.draft_id = None
        self.credentials = get_env_variable("GOOGLE_API_CREDENTIALS_PATH")

    def __enter__(self):
        creds = super().__enter__()
        if isinstance(creds, dict) and "auth_url" in creds:
            return creds

        self.gmail = build("gmail", "v1", credentials=creds)
        return self

    def create_draft(self, message, to, sender, subject):
        mime_message = EmailMessage()
        mime_message.set_content(message)
        mime_message["To"] = to
        mime_message["From"] = sender
        mime_message["Subject"] = subject
        encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
        create_message = {"message": {"raw": encoded_message}}
        draft = (
            self.gmail.users()
            .drafts()
            .create(userId="me", body=create_message)
            .execute()
        )
        self.draft_id = draft["id"]
        return draft

    def create_draft_with_attachment(self, message, to, sender, subject, attachment):
        mime_message = EmailMessage()
        mime_message["To"] = to
        mime_message["From"] = sender
        mime_message["Subject"] = subject

        mime_message.set_content(message)
        if attachment.startswith("http://") or attachment.startswith("https://"):
            response = requests.get(attachment)
            attachment_data = response.content
            filename = attachment.split("/")[-1]
            content_type = response.headers["Content-Type"]
        else:
            filename = os.path.basename(attachment)
            content_type, _ = mimetypes.guess_type(attachment)
            with open(attachment, "rb") as fp:
                attachment_data = fp.read()

        main_type, sub_type = (
            content_type.split("/", 1)
            if content_type
            else ("application", "octet-stream")
        )
        mime_message.add_attachment(
            attachment_data, maintype=main_type, subtype=sub_type, filename=filename
        )
        encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
        create_draft_request_body = {"message": {"raw": encoded_message}}
        try:
            draft = (
                self.gmail.users()
                .drafts()
                .create(userId="me", body=create_draft_request_body)
                .execute()
            )
            self.draft_id = draft["id"]
            return draft
        except HttpError as error:
            return None

    def send_send_message(self, message, to, sender, subject):
        mime_message = EmailMessage()
        mime_message.set_content(message)
        mime_message["To"] = to
        mime_message["From"] = sender
        mime_message["Subject"] = subject
        encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
        create_message = {"raw": encoded_message}
        send_message = (
            self.gmail.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        return send_message

    def send_send_message_with_attachment(
        self, message, to, sender, subject, attachment
    ):
        mime_message = EmailMessage()
        mime_message["To"] = to
        mime_message["From"] = sender
        mime_message["Subject"] = subject

        mime_message.set_content(message)
        if attachment.startswith("http://") or attachment.startswith("https://"):
            response = requests.get(attachment)
            attachment_data = response.content
            filename = attachment.split("/")[-1]
            content_type = response.headers["Content-Type"]
        else:
            filename = os.path.basename(attachment)
            content_type, _ = mimetypes.guess_type(attachment)
            with open(attachment, "rb") as fp:
                attachment_data = fp.read()

        main_type, sub_type = (
            content_type.split("/", 1)
            if content_type
            else ("application", "octet-stream")
        )
        mime_message.add_attachment(
            attachment_data, maintype=main_type, subtype=sub_type, filename=filename
        )
        encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
        create_message = {"raw": encoded_message}
        send_message = (
            self.gmail.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        return send_message

    def send_draft(self, draft_id):
        draft = (
            self.gmail.users()
            .drafts()
            .send(userId="me", body={"id": draft_id})
            .execute()
        )
        return draft

    def get_draft(self, draft_id):
        draft = (
            self.gmail.users()
            .drafts()
            .get(userId="me", id=draft_id)
            .execute()
        )
        return draft
    
    def delete_draft(self, draft_id):
        try:
            self.gmail.users().drafts().delete(userId="me", id=draft_id).execute()
            return True
        except HttpError as error:
            return False
        
    def data_encoder(self, text):
        if text and len(text)>0:
            message = base64.urlsafe_b64decode(text.encode('UTF8'))
            message = str(message, 'utf-8')
            message = email.message_from_string(message)
            return message
        else:
            return None

    def read_message(self, content)->str:
        if content.get('payload').get('parts', None):
            parts = content.get('payload').get('parts', None)
            sub_part = copy.deepcopy(parts[0])
            while sub_part.get("mimeType", None) != "text/plain":
                try:
                    sub_part = copy.deepcopy(sub_part.get('parts', None)[0])
                except Exception as e:
                    break
            return self.data_encoder(sub_part.get('body', None).get('data', None)).as_string()
        else:
            return content.get("snippet")

    def get_email_messages(self, target_email, page_token=None, page_size=10):
        try:
            if not target_email:
                raise ValueError("Sender email is required")

            received_params = {
                'userId': 'me',
                'maxResults': page_size,
                'q': f"from:{target_email}"
            }
            if page_token and '@' not in page_token:
                received_params['pageToken'] = page_token
            
            sent_params = {
                'userId': 'me',
                'maxResults': page_size,
                'q': f"to:{target_email}"
            }
            if page_token and '@' not in page_token:
                sent_params['pageToken'] = page_token

            messages_data = [] 
            received_messages = self.gmail.users().messages().list(**received_params).execute().get('messages', [])
            sent_messages = self.gmail.users().messages().list(**sent_params).execute().get('messages', [])

            all_messages = received_messages + sent_messages
            
            for email in all_messages:
                message = self.gmail.users().messages().get(userId='me', id=email['id'], format="full").execute()
                if not message:
                    continue
                data = self.read_message(content=message)
                _from = next((h for h in message.get('payload', {}).get('headers', []) if h['name'] == 'From'), None).get('value', None)
                _to = next((h for h in message.get('payload', {}).get('headers', []) if h['name'] == 'To'), None).get('value', None)
                date = next((h for h in message.get('payload', {}).get('headers', []) if h['name'] == 'Date'), None).get('value', None)
                messages_data.append({
                    'id': email['id'],
                    'body': data,
                    'type': 'received' if _from == target_email else 'sent',
                    'from': _from,
                    'to': _to,
                    'date': date,
                    'subject': next((h for h in message.get('payload', {}).get('headers', []) if h['name'] == 'Subject'), None).get('value', None),
                })
            
            # Sort messages by date
            messages_data.sort(key=lambda x: parsedate_to_datetime(x['date']) if x['date'] else datetime.min)
            return {
                'messages': messages_data
            }
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return None
    
    def subscribe_to_topic(self):
        try:
            request = {
                'labelIds': ['INBOX'],
                'topicName': 'projects/memorly-454105/topics/email-topic',
                'labelFilterBehavior': 'INCLUDE'
            }
            response = self.gmail.users().watch(userId='me', body=request).execute()
            return response
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def get_email_message_from_webhook(self, webhook_data):
        """
        Process webhook data from Gmail push notifications and retrieve the email message.
        
        Args:
            webhook_data (dict): The webhook payload containing message data
            
        Returns:
            dict: The email message details or None if an error occurs
        """
        try:
            encoded_data = webhook_data.get('message', {}).get('data', '')
            if not encoded_data:
                logger.error("No data found in webhook payload")
                return None
                
            decoded_data = base64.b64decode(encoded_data).decode('utf-8')
            data = json.loads(decoded_data)
            
            email_address = data.get('emailAddress')
            history_id = data.get('historyId')
            
            if not history_id:
                logger.error("No history ID found in decoded webhook data")
                return None
                
            history = self.gmail.users().history().list(
                userId='me',
                startHistoryId=history_id,
                historyTypes=['messageAdded']
            ).execute()
            
            if not history or 'history' not in history:
                logger.error(f"No history found for history ID: {history_id}")
                return None
                
            message_id = None
            for item in history.get('history', []):
                for message_added in item.get('messagesAdded', []):
                    message_id = message_added.get('message', {}).get('id')
                    if message_id:
                        break
                if message_id:
                    break
                    
            if not message_id:
                logger.error("No message ID found in history")
                return None
                
            message = self.gmail.users().messages().get(
                userId='me',
                id=message_id,
                format="full"
            ).execute()
            
            if not message:
                logger.error(f"Could not retrieve message with ID: {message_id}")
                return None
                
            data = self.read_message(content=message)
            _from = next((h for h in message.get('payload', {}).get('headers', []) if h['name'] == 'From'), None)
            _to = next((h for h in message.get('payload', {}).get('headers', []) if h['name'] == 'To'), None)
            date = next((h for h in message.get('payload', {}).get('headers', []) if h['name'] == 'Date'), None)
            subject = next((h for h in message.get('payload', {}).get('headers', []) if h['name'] == 'Subject'), None)
            
            return {
                'id': message_id,
                'body': data,
                'from': _from.get('value') if _from else None,
                'to': _to.get('value') if _to else None,
                'date': date.get('value') if date else None,
                'subject': subject.get('value') if subject else None,
                'raw_message': message
            }
            
        except Exception as e:
            logger.error(f"Error processing webhook data: {str(e)}")
            return None

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass
