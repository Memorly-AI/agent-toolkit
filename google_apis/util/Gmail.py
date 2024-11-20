import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import os
from email.message import EmailMessage
import mimetypes
import requests
from utils.constants import get_env_variable
from google_apis.util.Auth import Auth


class Gmail(Auth):

    def __init__(self, scopes=None):
        super().__init__(scopes)
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

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass
