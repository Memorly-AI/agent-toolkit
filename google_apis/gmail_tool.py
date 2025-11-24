from google_apis.util.Gmail import Gmail
from django.http import JsonResponse
from django.http.request import HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json


@csrf_exempt
@require_POST
def gmail_api(request: HttpRequest):
    try:
        data = json.loads(request.body)
        operation = data.get("operation")
        tool_id = data.get("tool_id")
        
        if not operation or not tool_id:
            return JsonResponse({
                "error": "Operation type and user ID are required",
                "status": False,
                "message": "Operation failed"
            }, status=400)

        message = data.get("message")
        to = data.get("to")
        sender = data.get("sender")
        subject = data.get("subject")
        
        with Gmail(tool_id) as gmail:
            if operation == "create_draft":
                if not message or not to or not sender or not subject:
                    return JsonResponse({
                        "error": "Required fields are missing",
                        "status": False,
                        "message": "Draft creation failed"
                    }, status=400)
                response = gmail.create_draft(message, to, sender, subject)
                success_message = "Draft created successfully"
                
            elif operation == "create_draft_with_attachment":
                attachment = data.get("attachment")
                if not message or not to or not sender or not subject or not attachment:
                    return JsonResponse({
                        "error": "Required fields are missing",
                        "status": False,
                        "message": "Draft creation failed"
                    }, status=400)
                response = gmail.create_draft_with_attachment(message, to, sender, subject, attachment)
                success_message = "Draft created successfully"
                
            elif operation == "send_message":
                if not message or not to or not sender or not subject:
                    return JsonResponse({
                        "error": "Required fields are missing",
                        "status": False,
                        "message": "Message send failed"
                    }, status=400)  
                response = gmail.send_send_message(message, to, sender, subject)
                success_message = "Message sent successfully"
                
            elif operation == "send_message_with_attachment":
                attachment = data.get("attachment")
                if not message or not to or not sender or not subject or not attachment:
                    return JsonResponse({
                        "error": "Required fields are missing",
                        "status": False,
                        "message": "Message send failed"
                    }, status=400)
                response = gmail.send_send_message_with_attachment(message, to, sender, subject, attachment)
                success_message = "Message sent successfully"
                
            elif operation == "send_draft":
                draft_id = data.get("draft_id")
                if not draft_id:
                    return JsonResponse({
                        "error": "Draft ID is missing",
                        "status": False,
                        "message": "Draft send failed"
                    }, status=400)
                response = gmail.send_draft(draft_id)
                success_message = "Draft sent successfully"
                
            elif operation == "get_draft":
                draft_id = data.get("draft_id")
                if not draft_id:
                    return JsonResponse({
                        "error": "Draft ID is missing",
                        "status": False,
                        "message": "Draft retrieval failed"
                    }, status=400)
                response = gmail.get_draft(draft_id)
                success_message = "Draft retrieved successfully"

            elif operation == "delete_draft":
                draft_id = data.get("draft_id")
                if not draft_id:
                    return JsonResponse({
                        "error": "Draft ID is missing",
                        "status": False,
                        "message": "Draft deletion failed"
                    }, status=400)
                response = gmail.delete_draft(draft_id)
                success_message = "Draft deleted successfully"

            elif operation == "get_emails":
                email_id = data.get("email_id")
                page_size = data.get("page_size", 10)
                if not email_id:
                    return JsonResponse({
                        "error": "Email ID is missing",
                        "status": False,
                        "message": "Email retrieval failed"
                    }, status=400)
                response = gmail.get_email_messages(email_id, page_size=page_size)
                success_message = "Emails retrieved successfully"

            else:
                return JsonResponse({
                    "error": f"Unknown operation: {operation}",
                    "status": False,
                    "message": "Operation failed"
                }, status=400)
            
            return JsonResponse({
                "result": response,
                "status": True,
                "message": success_message
            })     
    except Exception as e:
        operation_name = data.get("operation", "Unknown operation")
        return JsonResponse({
            "error": str(e),
            "status": False,
            "message": f"{operation_name} failed"
        })
    
