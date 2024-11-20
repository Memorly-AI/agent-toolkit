from googleapiclient.discovery import build
import os
from google_apis.util.Auth import Auth


class Sheet(Auth):
    def __init__(self, scopes: list = None):
        super().__init__(scopes)
        self.sheet = None

    def __enter__(self):
        creds = super().__enter__()
        if isinstance(creds, dict):
            return creds
        self.sheet = build("sheets", "v4", credentials=creds).spreadsheets()
        return self

    def create(self, title):
        spreadsheet = {"properties": {"title": title}}
        spreadsheet = self.sheet.create(body=spreadsheet).execute()
        return spreadsheet.get("spreadsheetId")

    def update_values(self, sheet_id, range_name, value_input_option, values):
        body = {"values": values}
        result = (
            self.sheet.values()
            .update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body=body,
            )
            .execute()
        )
        return result

    def append_values(self, sheet_id, range_name, value_input_option, values):
        """
        Append values to a Google Sheet with more detailed error handling and logging.
        
        Args:
            sheet_id (str): The ID of the spreadsheet
            range_name (str): The range to append values to (e.g., 'Sheet1!A:C')
            value_input_option (str): How to interpret the values (USER_ENTERED or RAW)
            values (list): 2D list of values to append
        
        Returns:
            dict: API response from the append operation
        """
        try:
            body = {
                "values": values,
                "majorDimension": "ROWS"  
            }
            if "!" not in range_name:
                range_name = f"Sheet1!{range_name}"
            
            result = (
                self.sheet.values()
                .append(
                    spreadsheetId=sheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    insertDataOption="INSERT_ROWS",  
                    body=body,
                )
                .execute()
            )
            return result
        except Exception as e:
            raise e

    def get_values(self, sheet_id, range_name):
        result = (
            self.sheet.values()
            .get(spreadsheetId=sheet_id, range=range_name)
            .execute()
        )
        return result

    def batch_update(self, sheet_id, title, find, replacement):
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
            spreadsheetId=sheet_id, body=body
        ).execute()
        return response

    def batch_update_values(self, sheet_id, range_name, value_input_option, _values):
        values = _values
        data = [{"range": range_name, "values": values}]
        body = {"valueInputOption": value_input_option, "data": data}
        result = (
            self.sheet.values()
            .batchUpdate(spreadsheetId=sheet_id, body=body)
            .execute()
        )
        return result

    def batch_get_values(self, sheet_id, range_names):
        result = (
            self.sheet.values()
            .batchGet(spreadsheetId=sheet_id, ranges=range_names)
            .execute()
        )
        return result

    def conditional_formatting(self, sheet_id, format=[]):
        body = {"requests": format}
        response = self.sheet.batchUpdate(
            spreadsheetId=sheet_id, body=body
        ).execute()
        return response

    def filter_views(self, sheet_id, range):
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
            spreadsheetId=sheet_id, body=body
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
            spreadsheetId=sheet_id, body=body
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
            spreadsheetId=sheet_id, body=body
        ).execute()
        return updatefilterviewresponse

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass
