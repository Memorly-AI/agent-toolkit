from googleapiclient.discovery import build
from google_apis.util.Auth import Auth


class Sheet(Auth):

    def __init__(self, user_id, apps = ['sheets']):
        super().__init__(user_id, apps=apps)
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
    
    
    def get_column_range(self, length):
        """
        Generate a column range in A1 notation based on the number of columns.
        
        Args:
            length (int): The number of columns to include in the range.
            
        Returns:
            str: The column range in A1 notation (e.g., "A:C").
        """
        if length < 1:
            raise ValueError("Length must be at least 1.")
        
        def column_letter(index):
            """Convert a 1-based index to a column letter (e.g., 1 -> A, 27 -> AA)."""
            letter = ""
            while index > 0:
                index -= 1
                letter = chr(index % 26 + ord('A')) + letter
                index //= 26
            return letter

        start_column = "A"
        end_column = column_letter(length)
        return f"{start_column}:{end_column}"


    def append_values(self, sheet_id, range_name, value_input_option, values):
        """
        Append values to a Google Sheet using the append API.
        """
        try:
            body = {"values": values, "majorDimension": "ROWS"}
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


    def update_values(self, sheet_id, range_name, value_input_option, values):
        """
        Update values in a specific range of a Google Sheet.
        """
        try:
            body = {"values": values, "majorDimension": "ROWS"}
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
    
    
    def find_row(self, sheet_id, search_keyword, range_name = None):
        """
        Searches for a keyword (or substring) in any column of the sheet and returns the row number.
        
        Args:
            sheet_id (str): The ID of the Google Sheet.
            search_keyword (str): The keyword or substring to search for.

        Returns:
            int or None: The row number where the keyword is found, or None if not found.
        """
        try:
            result = self.sheet.values().get(
                spreadsheetId=sheet_id,
                range=range_name if range_name else "A:Z"  
            ).execute()

            values = result.get("values", [])

            matching_rows = []
            for i, row in enumerate(values, start=1):
                for cell in row:
                    if search_keyword.lower() in str(cell).lower():
                        matching_rows.append(i)
                        break  # Move to the next row once a match is found

            return matching_rows if matching_rows else None
        except Exception as e:
            print(f"Error finding row: {e}")
            return None


    def find_columns(self, sheet_id, search_keyword):
        """
        Searches for a keyword in any row of the sheet and returns the column indexes where it appears.
        
        Args:
            sheet_id (str): The ID of the Google Sheet.
            search_keyword (str): The keyword or substring to search for.

        Returns:
            List[str]: Column letters (A, B, C, etc.) where the keyword is found.
        """
        try:
            result = self.sheet.values().get(
                spreadsheetId=sheet_id,
                range="A:Z"  # Fetch all columns
            ).execute()

            values = result.get("values", [])

            column_indexes = set()
            for row in values:
                for col_index, cell in enumerate(row):
                    if search_keyword.lower() in str(cell).lower():
                        column_letter = chr(65 + col_index)  # Convert index to A, B, C...
                        column_indexes.add(column_letter)

            return list(column_indexes) if column_indexes else None
        except Exception as e:
            return None


    def get_sheet_gid(self, sheet_id, sheet_name=None):
        """
        Retrieves the GID (grid ID) of the first sheet in the spreadsheet.
        """
        try:
            sheet_metadata = self.sheet.get(spreadsheetId=sheet_id).execute()
            sheets = sheet_metadata.get("sheets", [])

            if not sheets:
                raise ValueError("No sheets found in the spreadsheet.")

            if sheet_name:
                for sheet in sheets:
                    if sheet["properties"]["title"] == sheet_name:
                        return sheet["properties"]["sheetId"]   
                    
            return sheets[0]["properties"]["sheetId"] 
        except Exception as e:
            print(f"Error getting sheet GID: {e}")
            return None


    def delete_rows(self, sheet_id, row_numbers, sheet_name=None):
        """
        Deletes multiple rows from the Google Sheet in a single request.
        """
        try:
            sheet_gid = self.get_sheet_gid(sheet_id, sheet_name)  # Fetch sheet GID

            if sheet_gid is None:
                return {"error": "Failed to retrieve sheet GID"}

            # Sort row numbers in descending order to avoid shifting issues
            row_numbers.sort(reverse=True)

            requests = []
            for row_number in row_numbers:
                requests.append({
                    "deleteDimension": {
                        "range": {
                            "sheetId": sheet_gid,
                            "dimension": "ROWS",
                            "startIndex": row_number - 1,
                            "endIndex": row_number
                        }
                    }
                })

            request_body = {"requests": requests}

            response = self.sheet.batchUpdate(
                spreadsheetId=sheet_id,
                body=request_body
            ).execute()

            return response
        except Exception as e:
            print(f"Error deleting rows: {e}")
            return None


    def get_header(self, sheet_id, range_name):
        """
        Retrieves the header row from the specified range in the Google Sheet.
        
        Args:
            sheet_id (str): The ID of the Google Sheet.
            range_name (str): The range to retrieve the header from (e.g., "Sheet1!A1:Z1").
        
        Returns:
            List[str]: The header row values or None if not found.
        """
        try:
            result = self.sheet.values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            return result.get("values", [])[0] if result.get("values") else None
        except Exception as e:
            print(f"Error retrieving header: {e}")
            return None


    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

