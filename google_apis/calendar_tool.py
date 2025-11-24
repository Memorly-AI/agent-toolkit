from google_apis.util.Calendar import Calendar
from django.http import JsonResponse    
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import logging


logger = logging.getLogger("django")


@csrf_exempt
@require_POST
def google_calender_api(request):
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
        
        with Calendar(tool_id) as calender:
            if operation == "create_calender_event":
                return handle_google_calendar_event(calender, data)
            # elif operation == "update_calender_event":
            #     return handle_update_calender_event(meet, data)
            # elif operation == "delete_calender_event":
            #     return handle_delete_calender_event(meet, data)
            # elif operation == "get_calender_event_by_date":
            #     return get_calender_event_by_date(meet, data)
            # elif operation == "get_calender_event":
            #     return get_calender_event_details(meet, data)
            else:
                logger.error(f"Invalid operation attempted: {operation}")
                return JsonResponse({
                    "error": f"Invalid operation: {operation}",
                    "status": False,
                    "message": "Operation failed"
                }, status=400)

    except Exception as e:
        logger.error(f"Error in google_calender_api: {str(e)}")
        return JsonResponse({
            "error": str(e),
            "status": False,
            "message": "Operation failed"
        }, status=500)
    

def handle_google_calendar_event(calender:Calendar, data):
    summary = data.get("summary", "")
    start_time = data.get("start_time", None)
    end_time = data.get("end_time", None)
    attendees = data.get("attendees", [])
    description = data.get("description", "")

    if not summary or not start_time or not end_time :
        return JsonResponse({
            "error": "Missing required fields (summary, start_time, end_time, timezone)",
            "status": False,
            "message": "Meet creation failed"
        }, status=400)

    response = calender.create_google_calendar_event(
        summary, start_time, end_time, attendees, description
    )
    
    return JsonResponse({
        "result": response,
        "status": True,
        "message": "event created successfully"
    })

