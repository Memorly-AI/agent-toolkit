from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from utils.constants import get_env_variable
from google_apis.util.Constants import *
from utils.constants import get_env_variable
import json
from typing import Optional, Dict, Any
import logging
from googleapiclient.discovery import build
from google_apis.models import GoogleCredential
from .Constants import *


logger = logging.getLogger('django')
API_URL = get_env_variable("API_URL")


class Auth:

    def __init__(self, uid: str, apps: list = ['all'], meta_info: dict = None):
        self.uid = uid
        self.meta_info = meta_info if meta_info else {}
        self.apps = apps
        self.scopes = self.get_scopes()
        self.credentials = get_env_variable("GOOGLE_API_CREDENTIALS_PATH")
        self.creds = self.get_user_cred()

    def get_scopes(self) -> list:
        scopes = set()
        for app in self.apps:
            if app == "sheet":
                scopes.update(SHEET_SCOPES)
            elif app == "gmail":
                scopes.update(GMAIL_SCOPES)
            elif app == "meet" or app == "calendar":
                scopes.update(CALENDAR_SCOPES)
            elif app == "docs":
                scopes.update(DOCS_SCOPES)
            elif app == "drive":
                scopes.update(DRIVE_SCOPES)
            elif app == "all":
                scopes.update(SCOPES)
    
        extra_scopes = [
            "https://www.googleapis.com/auth/userinfo.email",
            "openid",
            "https://www.googleapis.com/auth/userinfo.profile"
        ]
        
        scopes.update(extra_scopes)
        scopes = list(scopes)
        if not scopes or len(scopes) == 0:
            scopes = SCOPES
        return scopes

    def get_user_cred(self) -> Optional[Credentials]:
        try:
            google_cred = GoogleCredential.objects.get(uuid=self.uid)
            if "meta_info" in google_cred.credential:
                self.meta_info = google_cred.credential.pop("meta_info")
            return Credentials.from_authorized_user_info(google_cred.credential, google_cred.credential.get("scopes", self.scopes))
        except Exception as e:
            logger.error(f"Error getting user credentials: {str(e)}")
            return None

    def get_user_email(self, credentials: Credentials) -> str:
        """Retrieve the user's email address using the credentials."""
        try:
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            email = user_info.get('email', '')
            return email
        except Exception as e:
            logger.error(f"Error fetching user email: {str(e)}")
            return ""

    def save_user_cred(self, creds: Credentials | str | Dict[str, Any]) -> None:
        try:
            if isinstance(creds, Credentials):
                if creds.valid:
                    email = self.get_user_email(creds)
                    if email:
                        if self.meta_info is None:
                            self.meta_info = {}
                        self.meta_info["email"] = email
                
                creds_json = json.loads(creds.to_json())
            else:
                creds_json = json.loads(creds) if isinstance(creds, str) else creds

            if self.meta_info:
                creds_json["meta_info"] = self.meta_info

            google_cred, created = GoogleCredential.objects.update_or_create(
                uuid=self.uid,
                defaults={"credential": creds_json}
            )
            google_cred.save()
        except Exception as e:
            logger.error(f"Error saving user credentials: {str(e)}")
            raise

    def remove_user_cred(self) -> None:
        """Remove user credentials from the token file."""
        try:
            google_cred = GoogleCredential.objects.get(uuid=self.uid)
            google_cred.delete()
        except Exception as e:
            logger.error(f"Error removing user credentials: {str(e)}")

    def refresh_token(self) -> bool:
        """Attempt to refresh the token. Returns True if successful, False otherwise."""
        try:
            if self.creds and self.creds.refresh_token:
                self.creds.refresh(Request())
                self.save_user_cred(self.creds)
                return True
            return False
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return False

    def check_auth(self) -> bool:
        """Check if the user is authenticated and handle token refresh if needed."""
        if not self.creds:
            return False

        missing_scopes = [scope for scope in self.scopes if scope not in self.creds.scopes]
        if missing_scopes:
            logger.info(f"Missing required scopes: {missing_scopes}")
            return False

        if not self.creds.valid:
            if self.creds.expired and self.creds.refresh_token:
                return self.refresh_token()
            return False

        return True

    def authorize(self, code: str) -> Dict[str, str]:
        """Handle the OAuth2 callback and token storage."""
        try:
            flow = Flow.from_client_secrets_file(
                self.credentials,
                scopes=self.scopes,
                redirect_uri=f"{API_URL}/api/google/oauth2_callback/"
            )
            flow.fetch_token(code=code)
            creds = flow.credentials
            
            # Get user email and store it with credentials
            email = self.get_user_email(creds)
            if email:
                if self.meta_info is None:
                    self.meta_info = {}
                self.meta_info["email"] = email
            
            self.save_user_cred(creds)
            return {
                "message": "Authorization successful",
                "authorized": True,
                "email": email
            }
        except Exception as e:
            logger.error(f"Authorization failed: {str(e)}")
            return {
                "message": f"Authorization failed: {str(e)}",
                "authorized": False,
            }

    def get_auth_url(self) -> str:
        """Generate the authorization URL for OAuth2 flow."""
        flow = Flow.from_client_secrets_file(
            self.credentials,
            scopes=self.scopes,
            redirect_uri=f"{API_URL}/api/google/oauth2_callback/"
        )
        auth_url, _ = flow.authorization_url(
            prompt='consent',
            state=f"uid={self.uid}&apps={','.join(self.apps)}",
        )
        return auth_url

    def __enter__(self):
        """Context manager entry point with authentication check."""
        if not self.check_auth():
            return {"auth_url": self.get_auth_url()}
        return self.creds

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass
