from google_apis.util.Meet import Meet
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json


@csrf_exempt
@require_POST
def google_meet_api(request):
    """
    Unified Google Meet API endpoint that handles multiple operations:
    - create_meet: Create a new Google Meet
    - update_meet: Update an existing Google Meet
    - delete_meet: Delete a Google Meet
    - get_all_meets: Retrieve all Google Meets
    - get_meets_by_date: Retrieve all Google Meets for a specific date
    
    Request Parameters:
    - `operation` (str): The operation to perform (required)
    - `tool_id` (str): Unique identifier for authentication (required)
    - Additional parameters based on the specific operation
    
    Response: Returns operation-specific results or an error message
    """
    try:
        data = json.loads(request.body)
        operation = data.get("operation")
        tool_id = data.get("tool_id")

        if not operation or not tool_id:
            return JsonResponse({
                "error": "Missing required fields (operation, tool_id)",
                "status": False,
                "message": "Operation failed"
            }, status=400)
        
        with Meet(tool_id) as meet:
            if isinstance(meet, dict) and "auth_url" in meet:
                return JsonResponse({"auth_url": meet["auth_url"]})
            
            if operation == "create_meet":
                return handle_create_meet(meet, data)
            elif operation == "update_meet":
                return handle_update_meet(meet, data)
            elif operation == "delete_meet":
                return handle_delete_meet(meet, data)
            elif operation == "get_meets_by_date":
                return get_meets_by_date(meet, data)
            elif operation == "get_meet":
                return get_meet_details(meet, data)
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


def handle_create_meet(meet: Meet, data):
    """Handle create_meet operation"""
    summary = data.get("summary", None)
    start_time = data.get("start_time", None)
    end_time = data.get("end_time", None)
    timezone = data.get("timezone", None)

    if not summary or not start_time or not end_time or not timezone:
        return JsonResponse({
            "error": "Missing required fields (summary, start_time, end_time, timezone)",
            "status": False,
            "message": "Meet creation failed"
        }, status=400)
    
    response = meet.create(summary, start_time, end_time, timezone)
    return JsonResponse({
        "result": response,
        "status": True,
        "message": "Meet created successfully"
    })


def handle_update_meet(meet: Meet, data):
    """Handle update_meet operation"""
    meet_id = data.get("meet_id", None)
    meeting_link = data.get("meeting_link", None)
    summary = data.get("summary", None)
    start_time = data.get("start_time", None)
    end_time = data.get("end_time", None)
    timezone = data.get("timezone", None)
    
    if not summary or not start_time or not end_time or not timezone or (not meet_id and not meeting_link):
        return JsonResponse({
            "error": "Missing required fields (meet_id, summary, start_time, end_time, timezone)",
            "status": False,
            "message": "Meet update failed"
        }, status=400)
    
    if meeting_link:
        response = meet.update_by_meeting_link(meeting_link, summary, start_time, end_time, timezone)
    else:
        response = meet.update(meet_id, summary, start_time, end_time, timezone)
    return JsonResponse({
        "result": response,
        "status": True,
        "message": "Meet updated successfully"
    })


def handle_delete_meet(meet: Meet, data):
    """Handle delete_meet operation"""
    meet_id = data.get("meet_id", None)
    meeting_link = data.get("meeting_link", None)
    
    if not meet_id and not meeting_link:
        return JsonResponse({
            "error": "Missing required field (meet_id or meeting_link)",
            "status": False,
            "message": "Meet deletion failed"
        }, status=400)
    
    if meeting_link:
        response = meet.delete_by_meeting_link(meeting_link)
    else:
        response = meet.delete(meet_id)
    return JsonResponse({
        "result": response,
        "status": True,
        "message": "Meet deleted successfully"
    })


def get_meets_by_date(meet: Meet, data):
    """Handle get_meets_by_date operation"""
    start_date = data.get("start_date", None)
    end_date = data.get("end_date", None)
    
    if not start_date or not end_date:
        return JsonResponse({
            "error": "Missing required fields (start_date, end_date)",
            "status": False,
            "message": "Meet retrieval failed"
        }, status=400)
    
    response = meet.get_meeting_by_date(start_date, end_date)
    return JsonResponse({
        "result": response,
        "status": True,
        "message": "Meets retrieved successfully"
    })


def get_meet_details(meet: Meet, data):
    """Handle get_meet_by_id operation"""
    meet_id = data.get("meet_id", None)
    meeting_link = data.get("meeting_link", None)
    
    if not meet_id and not meeting_link:
        return JsonResponse({
            "error": "Missing required field (meet_id or meeting_link)",
            "status": False,
            "message": "Meet retrieval failed"
        }, status=400)
    
    if meeting_link:
        response = meet.get_meeting_by_link(meeting_link)
    else:
        response = meet.get_meeting_by_id(meet_id)
    return JsonResponse({
        "result": response,
        "status": True,
        "message": "Meet retrieved successfully"
    })


# Usage:
# POST request to google_meet_api endpoint with JSON data:
# {
#     "operation": "create_meet",
#     "tool_id": "1",
#     "summary": "Team Meeting",
#     "start_time": "2022-12-01T09:00:00",
#     "end_time": "2022-12-01T10:00:00",
#     "timezone": "Asia/Kolkata"
# }

# POST request to google_meet_api endpoint with JSON data:
# {
#     "operation": "delete_meet",
#     "tool_id": "1",
#     "meet_id": "meet_id"
# }

# POST request to google_meet_api endpoint with JSON data:
# {
#     "operation": "get_meets_by_date",
#     "tool_id": "1",
#     "start_date": "2022-12-01T00:00:00",
#     "end_date": "2022-12-01T23:59:59"
# }

# POST request to google_meet_api endpoint with JSON data:
# {
#     "operation": "update_meet",
#     "tool_id": "1",
#     "meet_id": "meet_id",
#     "summary": "Updated Team Meeting",
#     "start_time": "2022-12-01T10:00:00",
#     "end_time": "2022-12-01T11:00:00",
#     "timezone": "Asia/Kolkata"
# }

# POST request to google_meet_api endpoint with JSON data:
# {
#     "operation": "get_meet",
#     "tool_id": "1",
#     "meet_id": "meet_id"
# }
