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


class Gmail:
    def __init__(self, scopes=None):
        self.gmail = None
        self.draft_id = None
        self.credentials = get_env_variable("GOOGLE_API_CREDENTIALS_PATH")
        if scopes is not None:
            self.SCOPES = scopes
        else:
            self.SCOPES = [
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/gmail.compose",
                "https://www.googleapis.com/auth/gmail.modify",
                "https://www.googleapis.com/auth/gmail.metadata",
                "https://www.googleapis.com/auth/gmail.labels",
            ]

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
            self.gmail = build("gmail", "v1", credentials=creds)
            return self
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error

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
        print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')
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
            print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')
            return draft
        except HttpError as error:
            print(f"An error occurred: {error}")
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
        print(f'Message Id: {send_message["id"]}')
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
        print(f'Message Id: {send_message["id"]}')
        return send_message

    def send_draft(self, draft_id):
        draft = (
            self.gmail.users()
            .drafts()
            .send(userId="me", body={"id": draft_id})
            .execute()
        )
        print(f"Draft sent: {draft}")
        return draft

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

