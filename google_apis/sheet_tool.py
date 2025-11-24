import json
from google_apis.util.Sheet import Sheet
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def google_sheets_api(request):
    """
    Unified Google Sheets API endpoint that handles multiple operations:
    - append_values: Append values to a sheet
    - update_values: Update values in a sheet
    - get_values: Retrieve values from a sheet
    - search_by_keyword: Search for a keyword in rows or columns
    - update_cell_by_keyword: Update a cell based on a keyword search
    - delete_by_keyword: Delete rows or cells based on a keyword search
    
    Request Parameters:
    - `operation` (str): The operation to perform (required)
    - `sheet_id` (str): ID of the Google Sheet (required)
    - `tool_id` (str): ID of the tool (required)
    - Additional parameters based on the specific operation
    
    Response: Returns operation-specific results or an error message
    """
    try:
        data = json.loads(request.body)
        operation = data.get("operation")
        sheet_id = data.get("sheet_id")
        tool_id = data.get("tool_id")

        missing_fields = []
        if not operation:
            missing_fields.append('operation')
        if not sheet_id:
            missing_fields.append('sheet_id')
        if not tool_id:
            missing_fields.append('tool_id')

        if missing_fields:
            return JsonResponse({"error": f"Please provide the following fields: {', '.join(missing_fields)}"}, status=400)
        
        with Sheet(tool_id) as sheet:
            if operation == "append_values" or operation == "update_values":
                return handle_write_values(sheet, data)
            elif operation == "get_values":
                return handle_get_values(sheet, data)
            elif operation == "search_by_keyword":
                return handle_search_by_keyword(sheet, data)
            elif operation == "update_cell_by_keyword":
                return handle_update_cell_by_keyword(sheet, data)
            elif operation == "update_row_by_keyword":
                return handle_update_row_by_keyword(sheet, data)
            elif operation == "delete_by_keyword":
                return handle_delete_by_keyword(sheet, data)
            else:
                return JsonResponse({
                    "error": f"Invalid operation: {operation}",
                    "status": False,
                    "message": "Operation failed"
                }, status=400)
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "status": False,
            "message": "Operation failed"
        }, status=500)


def handle_write_values(sheet, data):
    """Handle append_values and update_values operations"""
    operation = data.get("operation", None)
    range_name = data.get("range_name", None)  # e.g., "Sheet1!A1", "Sheet1!A:C"
    value_input_option = data.get("value_input_option", "USER_ENTERED")
    values = data.get("values", [])
    sheet_id = data.get("sheet_id", None)
    
    if not range_name or not values or not sheet_id or not operation:
        return JsonResponse({
            "error": "Missing required fields (range_name, values, sheet_id, operation)",
            "status": False,
            "message": "Operation failed"
        }, status=400)
    
    if operation == "append_values":
        response = sheet.append_values(sheet_id, range_name, value_input_option, values)
    else:  # update_values
        response = sheet.update_values(sheet_id, range_name, value_input_option, values)
    
    return JsonResponse({
        "result": response,
        "status": True,
        "message": f"Values {operation.split('_')[0]}ed successfully"
    })
    

def handle_get_values(sheet, data):
    """Handle get_values operation"""
    range_name = data.get("range_name", None)
    sheet_id = data.get("sheet_id", None)
    
    if not range_name or not sheet_id:
        return JsonResponse({
            "error": "Missing required field (range_name or sheet_id)",           
            "status": False,
            "message": "Values retrieval failed"
        }, status=400)
    
    response = sheet.get_values(sheet_id, range_name)
    return JsonResponse({
        "result": response,
        "status": True,
        "message": "Values retrieved successfully"
    })


def handle_search_by_keyword(sheet: Sheet, data):
    """Handle search_by_keyword operation"""
    sheet_id = data.get("sheet_id")
    search_keyword = data.get("search_keyword", "").lower()  # Convert to lowercase for case-insensitive search
    search_type = data.get("search_type", "row")  # "row" or "column"
    _range_name = data.get("range_name", None)
    
    if not search_keyword or not _range_name:
        return JsonResponse({
            "error": "Missing required field (search_keyword or range_name)",
            "status": False,
            "message": "Search failed"
        }, status=400)

    sheet_name = _range_name.split("!")[0] if "!" in _range_name else "Sheet1"

    if search_type == "row":
        row_numbers = sheet.find_row(sheet_id, search_keyword, _range_name)
        if not row_numbers:
            return JsonResponse({
                "error": "Keyword not found in any row",
                "status": False,
                "message": "Search failed"
            }, status=404)

        range_names = [f"{sheet_name}!{row}:{row}" for row in row_numbers] 
        row_data = sheet.batch_get_values(sheet_id, range_names)
        extracted_data = [item.get("values", []) for item in row_data.get("valueRanges", [])]
        flattened_data = [row[0] for row in extracted_data if row]  
        
    elif search_type == "column":
        col_indexes = sheet.find_columns(sheet_id, search_keyword)
        if not col_indexes:
            return JsonResponse({
                "error": "Keyword not found in any column",
                "status": False,
                "message": "Search failed"
            }, status=404)

        range_names = [f"{sheet_name}!{col}:{col}" for col in col_indexes]  
        col_data = sheet.batch_get_values(sheet_id, range_names)
        extracted_data = [item.get("values", []) for item in col_data.get("valueRanges", [])]

        filtered_data = []
        for col in extracted_data:
            matches = [cell for cell in col if search_keyword in str(cell[0]).lower()]
            if matches:
                filtered_data.append(matches)  

        flattened_data = filtered_data if filtered_data else []
        header_row = sheet.get_header(sheet_id, _range_name)
        for data in flattened_data:
            if len(data) < len(header_row):
                data += [""] * (len(header_row) - len(data))
        flattened_data.insert(0, header_row) 
    else:
        return JsonResponse({
            "error": "Invalid search_type. Use 'row' or 'column'.",
            "status": False,
            "message": "Search failed"
        }, status=400)  

    return JsonResponse({
        "result": flattened_data,
        "status": True,
        "message": f"Search successful for {search_type}"
    })


def handle_update_cell_by_keyword(sheet: Sheet, data):
    """Handle update_cell_by_keyword operation"""
    sheet_id = data.get("sheet_id")
    search_keyword = data.get("search_keyword")
    column = data.get("column") 
    single_update = data.get("single_update", False)
    new_value = data.get("value", None)  
    _range_name = data.get("range_name", None)
    
    if not all([search_keyword, column, new_value, _range_name]):
        return JsonResponse({
            "error": "Missing required fields (search_keyword, column, value, range_name)",
            "status": False,
            "message": "Update failed"
        }, status=400)
    
    row_numbers = sheet.find_row(sheet_id, search_keyword, _range_name)  # Find all matching rows
    if not row_numbers:
        return JsonResponse({
            "error": "Keyword not found in sheet",
            "status": False,
            "message": "Update failed"
        }, status=404)
        
    if single_update:
        row_numbers = [row_numbers[0]]  # Keep only the first match

    sheet_name = _range_name.split("!")[0] if "!" in _range_name else "Sheet1"

    responses = []
    for row_number in row_numbers:
        range_name = f"{sheet_name}!{column}{row_number}"
        response = sheet.update_values(sheet_id, range_name, "USER_ENTERED", [[new_value]])
        responses.append({f"{column}{row_number}": response})

    return JsonResponse({
        "result": responses,
        "status": True,
        "message": f"Updated {len(row_numbers)} cell(s) successfully"
    })


def handle_update_row_by_keyword(sheet: Sheet, data):
    """Handle update_cell_by_keyword operation"""
    sheet_id = data.get("sheet_id")
    search_keyword = data.get("search_keyword", None)
    search_by_session_id = data.get("search_by_session_id", False)
    session_id = data.get("session_id", None)
    single_update = data.get("single_update", False)
    _range_name = data.get("range_name", None)
    values = data.get("values", None)  
    value_input_option = data.get("value_input_option", "USER_ENTERED")
    
    if search_by_session_id:
        search_keyword = session_id
    
    if not all([search_keyword, _range_name, values, value_input_option, sheet_id]):
        return JsonResponse({
            "error": "Missing required fields (search_keyword, range_name, values, value_input_option, sheet_id)",
            "status": False,
            "message": "Update failed"
        }, status=400)
    
    row_numbers = sheet.find_row(sheet_id, search_keyword, _range_name)  # Find all matching rows

    if not row_numbers:
        response = sheet.append_values(sheet_id, _range_name, value_input_option, values)
        return JsonResponse({
            "result": response,
            "status": True,
            "message": "Keyword not found, new row created successfully"
        })
        
    if single_update:
        row_numbers = [row_numbers[0]]  # Keep only the first match

    sheet_name = _range_name.split("!")[0] if "!" in _range_name else "Sheet1"

    responses = []
    for row_number in row_numbers:
        range_name = f"{sheet_name}!{row_number}:{row_number}"  # Update the entire row
        if len(values) == 0:
            return JsonResponse({
                "error": "Values cannot be empty for row update",
                "status": False,
                "message": "Update failed"
            })
        if len(values) > 1:
            return JsonResponse({
                "error": "Values should be a single list for row update",
                "status": False,
                "message": "Update failed"
            }, status=400)
        if len(values[0]) == 0:
            return JsonResponse({
                "error": "Values cannot be empty for row update",
                "status": False,
                "message": "Update failed"
            }, status=400)
            
        response = sheet.update_values(sheet_id, range_name, value_input_option, values)
        responses.append({f"{row_number}": response})
        
    if not responses:
        return JsonResponse({
            "error": "No rows updated",
            "status": False,
            "message": "Update failed"
        }, status=404)

    return JsonResponse({
        "result": responses,
        "status": True,
        "message": f"Updated {len(row_numbers)} cell(s) successfully"
    })


def handle_delete_by_keyword(sheet: Sheet, data):
    """Handle delete_by_keyword operation"""
    sheet_id = data.get("sheet_id")
    search_keyword = data.get("search_keyword")
    delete_type = data.get("delete_type", "row")  # "row" or "cell"
    column = data.get("column", None) if delete_type == "cell" else None
    single_delete = data.get("single_delete", False)
    range_name = data.get("range_name", None)
    
    if not search_keyword or not range_name or not sheet_id:
        return JsonResponse({
            "error": "Missing required field (search_keyword or range_name or sheet_id)",
            "status": False,
            "message": "Deletion failed"
        }, status=400)
    
    row_numbers = sheet.find_row(sheet_id, search_keyword, range_name)  # Find all matching rows
    if not row_numbers:
        return JsonResponse({
            "error": "Keyword not found in sheet",
            "status": False,
            "message": "Deletion failed"
        }, status=404)

    if single_delete:
        row_numbers = [row_numbers[0]]  # Only delete the first matching row/cell

    sheet_name = range_name.split("!")[0] if "!" in range_name else None
    if not sheet_name:
        return JsonResponse({
            "error": "Invalid range_name",
            "status": False,
            "message": "Deletion failed"
        }, status=400)

    if delete_type == "row":
        response = sheet.delete_rows(sheet_id, row_numbers, sheet_name)
    elif delete_type == "cell" and column:
        responses = []
        for row in row_numbers:
            _range_name = f"{sheet_name}!{column}{row}"
            responses.append(sheet.update_values(sheet_id, _range_name, "USER_ENTERED", [[""]]))  # Clear cell
        response = {"result": responses}
    else:
        return JsonResponse({
            "error": "Invalid delete_type or missing column for cell deletion",
            "status": False,
            "message": "Deletion failed"
        }, status=400)

    return JsonResponse({
        "result": response,
        "status": True,
        "message": f"{delete_type.capitalize()} deletion successful"
    })