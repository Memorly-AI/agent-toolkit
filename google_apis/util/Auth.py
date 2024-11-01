import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
import os
from utils.constants import get_env_variable
from google_apis.util.Constants import SCOPES


class Auth:
    def __init__(self, scopes: list = None):
        self.credentials = get_env_variable("GOOGLE_API_CREDENTIALS_PATH")
        self.SCOPES = scopes
        if self.SCOPES is None or len(self.SCOPES) == 0:
            self.SCOPES = SCOPES

    def authorize(self, code):
        flow = Flow.from_client_secrets_file(
            self.credentials, 
            scopes=self.SCOPES, 
            redirect_uri="http://127.0.0.1:8000/api/google/oauth2_callback/"
        )
        flow.fetch_token(code=code)
        creds = flow.credentials
        with open("token.json", "w") as token:
            token.write(creds.to_json())

        return {
            "message": "Authorization successful",
        }
    
    def __enter__(self):
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = Flow.from_client_secrets_file(
                    self.credentials, scopes=self.SCOPES,
                    redirect_uri="http://127.0.0.1:8000/api/google/oauth2_callback/"
                )
                auth_url, _ = flow.authorization_url(prompt='consent')
                return {"auth_url": auth_url}
        return creds
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass
