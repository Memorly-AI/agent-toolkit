from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import json
from google_apis.util.Auth import Auth


class Doc(Auth):

    def __init__(self, scopes=None):
        super().__init__(scopes)
        self.doc = None

    def __enter__(self):
        creds = super().__enter__()
        if isinstance(creds, dict) and "auth_url" in creds:
            return creds

        self.doc = build("docs", "v1", credentials=creds).documents()
        return self

    def get(self, doc_id):
        """
        Get the content of the Google Doc.

        Returns:
            dict: The content of the Google Doc
        """
        result = self.doc.get(documentId=doc_id).execute()
        return result

    def create(self, title, initial_text=None):
        """
        Create a new Google Doc with a title and optional initial text.
        
        Args:
            title (str): The title of the document
            initial_text (str, optional): Initial text to add to the document
        """
        doc = self.doc.create(body={"title": title}).execute()
        doc_id = doc["documentId"]
        
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
                    documentId=doc_id,
                    body={
                        "requests": requests
                    }
                ).execute()
            except HttpError as error:
                raise Exception(f"An error occurred: {error}")

        return doc_id
    
    def get_end_index(self, doc_id):
        doc_info = self.doc.get(documentId=doc_id).execute()
        return doc_info['body']['content'][-1]['endIndex']

    def add_content(self, doc_id, text, newlines=1):
        """
        Add content to the document with specified number of newlines.
        
        Args:
            text (str): The text to add to the document
            newlines (int, optional): Number of newlines to add after the text. Defaults to 1.
        """
        end_index = self.get_end_index(doc_id)
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
            documentId=doc_id,
            body={"requests": requests}
        ).execute()
        return result
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass
