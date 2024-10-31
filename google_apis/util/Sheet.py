import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from utils.constants import get_env_variable


class Sheet:
    def __init__(self, title, scopes=None):
        self.title = title
        self.sheet_id = None
        self.credentials = get_env_variable("GOOGLE_API_CREDENTIALS_PATH")
        self.sheet = None
        if scopes is not None:
            self.SCOPES = scopes
        else:
            self.SCOPES = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
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
            service = build("sheets", "v4", credentials=creds)
            self.sheet = service.spreadsheets()
            return self
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error

    def create(self):
        spreadsheet = {"properties": {"title": self.title}}
        spreadsheet = self.sheet.create(
            body=spreadsheet, fields="spreadsheetId"
        ).execute()
        self.sheet_id = spreadsheet.get("spreadsheetId")
        return spreadsheet.get("spreadsheetId")

    def update_values(self, range_name, value_input_option, values):
        body = {"values": values}
        result = (
            self.sheet.values()
            .update(
                spreadsheetId=self.sheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body=body,
            )
            .execute()
        )
        print(f"{result.get('updatedCells')} cells updated.")
        return result

    def append_values(self, range_name, value_input_option, values):
        body = {"values": values}
        result = (
            self.sheet.values()
            .append(
                spreadsheetId=self.sheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body=body,
            )
            .execute()
        )
        print(f"{result.get('updates').get('updatedCells')} cells appended.")
        return result

    def get_values(self, range_name):
        result = (
            self.sheet.values()
            .get(spreadsheetId=self.sheet_id, range=range_name)
            .execute()
        )
        rows = result.get("values", [])
        print(f"{len(rows)} rows retrieved")
        return result

    def batch_update(self, title, find, replacement):
        requests = []
        requests.append(
            {
                "updateSpreadsheetProperties": {
                    "properties": {"title": title},
                    "fields": "title",
                }
            }
        )
        requests.append(
            {
                "findReplace": {
                    "find": find,
                    "replacement": replacement,
                    "allSheets": True,
                }
            }
        )
        body = {"requests": requests}
        response = self.sheet.batchUpdate(
            spreadsheetId=self.sheet_id, body=body
        ).execute()
        find_replace_response = response.get("replies")[1].get("findReplace")
        print(f"{find_replace_response.get('occurrencesChanged')} replacements made.")
        return response

    def batch_update_values(self, range_name, value_input_option, _values):
        values = _values
        data = [{"range": range_name, "values": values}]
        body = {"valueInputOption": value_input_option, "data": data}
        result = (
            self.sheet.values()
            .batchUpdate(spreadsheetId=self.sheet_id, body=body)
            .execute()
        )
        print(f"{result.get('totalUpdatedCells')} cells updated.")
        return result

    def batch_get_values(self, range_names):
        result = (
            self.sheet.values()
            .batchGet(spreadsheetId=self.sheet_id, ranges=range_names)
            .execute()
        )
        ranges = result.get("valueRanges", [])
        print(f"{len(ranges)} ranges retrieved")
        return result

    def conditional_formatting(self, format=[]):
        body = {"requests": format}
        response = self.sheet.batchUpdate(
            spreadsheetId=self.sheet_id, body=body
        ).execute()
        print(f"{len(response.get('replies'))} cells updated.")
        return response

    def filter_views(self, range):
        addfilterviewrequest = {
            "addFilterView": {
                "filter": {
                    "title": "Sample Filter",
                    "range": range,
                    "sortSpecs": [
                        {
                            "dimensionIndex": 3,
                            "sortOrder": "DESCENDING",
                        }
                    ],
                    "criteria": {
                        0: {"hiddenValues": ["Panel"]},
                        6: {
                            "condition": {
                                "type": "DATE_BEFORE",
                                "values": {"userEnteredValue": "4/30/2016"},
                            }
                        },
                    },
                }
            }
        }

        body = {"requests": [addfilterviewrequest]}
        addfilterviewresponse = self.sheet.batchUpdate(
            spreadsheetId=self.sheet_id, body=body
        ).execute()

        duplicatefilterviewrequest = {
            "duplicateFilterView": {
                "filterId": addfilterviewresponse["replies"][0]["addFilterView"][
                    "filter"
                ]["filterViewId"]
            }
        }

        body = {"requests": [duplicatefilterviewrequest]}
        duplicatefilterviewresponse = self.sheet.batchUpdate(
            spreadsheetId=self.sheet_id, body=body
        ).execute()

        updatefilterviewrequest = {
            "updateFilterView": {
                "filter": {
                    "filterViewId": duplicatefilterviewresponse["replies"][0][
                        "duplicateFilterView"
                    ]["filter"]["filterViewId"],
                    "title": "Updated Filter",
                    "criteria": {
                        0: {},
                        3: {
                            "condition": {
                                "type": "NUMBER_GREATER",
                                "values": {"userEnteredValue": "5"},
                            }
                        },
                    },
                },
                "fields": {"paths": ["criteria", "title"]},
            }
        }

        body = {"requests": [updatefilterviewrequest]}
        updatefilterviewresponse = self.sheet.batchUpdate(
            spreadsheetId=self.sheet_id, body=body
        ).execute()
        print(str(updatefilterviewresponse))

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

