import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import json
from utils.constants import get_env_variable


class Doc:
    def __init__(self, scopes=None):
        self.doc_id = None
        self.doc = None
        self.credentials = get_env_variable("GOOGLE_API_CREDENTIALS_PATH")
        if scopes is not None:
            self.SCOPES = scopes
        else:
            self.SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]

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
            service = build("docs", "v1", credentials=creds)
            self.doc = service.documents()
            return self
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error

    def get(self):
        """
        Get the content of the Google Doc.

        Returns:
            dict: The content of the Google Doc
        """
        result = self.doc.get(documentId=self.doc_id).execute()
        print(json.dumps(result, indent=4, sort_keys=True))
        return result

    def create(self, title, initial_text=None):
        """
        Create a new Google Doc with a title and optional initial text.
        
        Args:
            title (str): The title of the document
            initial_text (str, optional): Initial text to add to the document
        """
        doc = self.doc.create(body={"title": title}).execute()
        self.doc_id = doc["documentId"]
        print(f"Document created with ID: {self.doc_id}")
        
        if initial_text:
            requests = [{
                "insertText": {
                    "location": {
                        "index": 1  
                    },
                    "text": initial_text
                }
            }]
            
            try:
                self.doc.batchUpdate(
                    documentId=self.doc_id,
                    body={
                        "requests": requests
                    }
                ).execute()
                print(f"Added initial text to document: {self.doc_id}")
            except HttpError as error:
                print(f"Error adding initial text: {error}")
                raise

        return doc
    
    def get_end_index(self):
        doc_info = self.doc.get(documentId=self.doc_id).execute()
        return doc_info['body']['content'][-1]['endIndex']

    def add_content(self, text, newlines=1):
        """
        Add content to the document with specified number of newlines.
        
        Args:
            text (str): The text to add to the document
            newlines (int, optional): Number of newlines to add after the text. Defaults to 1.
        """
        end_index = self.get_end_index()
        newline_chars = "\n" * newlines
        requests = [
            {
                "insertText": {
                    "location": {"index": end_index - 1},  
                    "text": f"{newline_chars}{text}"
                }
            }
        ]
        result = self.doc.batchUpdate(
            documentId=self.doc_id,
            body={"requests": requests}
        ).execute()
        print(f"Updated document with ID: {self.doc_id}")
        return result
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass


