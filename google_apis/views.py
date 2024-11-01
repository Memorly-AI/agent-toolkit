from google_apis.util.Sheet import Sheet
from google_apis.util.Meet import Meet
from google_apis.util.Gmail import Gmail
from google_apis.util.Auth import Auth
from google_apis.util.Doc import Doc
from django.http import JsonResponse
from django.http.request import HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import json


@csrf_exempt
@require_GET
def oauth2_callback(request: HttpRequest):
    try:
        code = request.GET.get("code") 
        if not code:
            return JsonResponse({"error": "Authorization code not provided"}, status=400)
        auth = Auth()
        response = auth.authorize(code)
        return JsonResponse({"response": response})
    except Exception as e:
        return JsonResponse({"error": str(e)})
    

@csrf_exempt
@require_POST
def create_new_sheet(request: HttpRequest):
    try:
        data = json.loads(request.body)
        title = data.get("title")
        with Sheet() as sheet:
            if isinstance(sheet, dict) and "auth_url" in sheet:
                return JsonResponse({"auth_url": sheet["auth_url"]})
            
            response = sheet.create(title)
            return JsonResponse({
                "result": response,
                "status": True,
                "message": "Sheet created successfully"
            }, status=200)
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "status": False,
            "message": "Sheet creation failed"
        }, status=400)
    

@csrf_exempt
@require_POST
def update_values(request: HttpRequest, sheet_id: str):
    try:
        data = json.loads(request.body)
        range_name = data.get("range_name")
        value_input_option = data.get("value_input_option")
        values = data.get("values")
        with Sheet() as sheet:
            response = sheet.update_values(sheet_id, range_name, value_input_option, values)
            return JsonResponse({
                "result": response,
                "status": True,
                "message": "Values updated successfully"
            })
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "status": False,
            "message": "Values update failed"
        })
    

@csrf_exempt
@require_POST
def append_values(request: HttpRequest, sheet_id: str):
    try:
        data = json.loads(request.body)
        range_name = data.get("range_name")
        value_input_option = data.get("value_input_option")
        values = data.get("values")
        with Sheet() as sheet:
            response = sheet.append_values(sheet_id, range_name, value_input_option, values)
            return JsonResponse({
                "result": response,
                "status": True,
                "message": "Values appended successfully"
            })
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "status": False,
            "message": "Values append failed"
        })
    

@csrf_exempt
@require_POST
def get_values(request: HttpRequest, sheet_id: str):
    try:
        data = json.loads(request.body)
        range_name = data.get("range_name")
        with Sheet() as sheet:
            response = sheet.get_values(sheet_id, range_name)
            return JsonResponse({
                "result": response,
                "status": True,
                "message": "Values retrieved successfully"
            })
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "status": False,
            "message": "Values retrieval failed"
        })
    

@csrf_exempt
@require_POST
def batch_update(request: HttpRequest, sheet_id: str):
    try:
        data = json.loads(request.body)
        title = data.get("title")
        find = data.get("find")
        replacement = data.get("replacement")
        with Sheet() as sheet:
            response = sheet.batch_update(sheet_id, title, find, replacement)
            return JsonResponse({
                "result": response,
                "status": True,
                "message": "Values updated successfully"
            })
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "status": False,
            "message": "Values update failed"
        })
    

@csrf_exempt
@require_POST
def batch_update_values(request: HttpRequest, sheet_id: str):
    try:
        data = json.loads(request.body)
        range_name = data.get("range_name")
        value_input_option = data.get("value_input_option")
        values = data.get("values")
        with Sheet() as sheet:
            response = sheet.batch_update_values(sheet_id, range_name, value_input_option, values)
            return JsonResponse({
                "result": response,
                "status": True,
                "message": "Values updated successfully"
            })
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "status": False,
            "message": "Values update failed"
        })
    

@csrf_exempt
@require_POST
def batch_get_values(request: HttpRequest, sheet_id: str):
    try:
        data = json.loads(request.body)
        range_names = data.get("range_names")
        with Sheet() as sheet:
            response = sheet.batch_get_values(sheet_id, range_names)
            return JsonResponse({
                "result": response,
                "status": True,
                "message": "Values retrieved successfully"
            })
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "status": False,
            "message": "Values retrieval failed"
        })
    

@csrf_exempt
@require_POST
def conditional_formatting(request: HttpRequest, sheet_id: str):
    try:
        data = json.loads(request.body)
        format = data.get("format")
        with Sheet() as sheet:
            response = sheet.conditional_formatting(sheet_id, format)
            return JsonResponse({
                "result": response,
                "status": True,
                "message": "Conditional formatting applied successfully"
            })
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "status": False,
            "message": "Conditional formatting failed"
        })
    

@csrf_exempt
@require_POST
def filter_views(request: HttpRequest, sheet_id: str):
    try:
        data = json.loads(request.body)
        range = data.get("range")
        with Sheet() as sheet:
            response = sheet.filter_views(sheet_id, range)
            return JsonResponse({
                "result": response,
                "status": True,
                "message": "Filter views applied successfully"
            })
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "status": False,
            "message": "Filter views failed"
        })


@csrf_exempt
@require_POST
def create_meet(request: HttpRequest):
    try:
        data = json.loads(request.body)
        summary = data.get("summary")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        timezone = data.get("timezone")
        with Meet() as meet:
            if isinstance(meet, dict) and "auth_url" in meet:
                return JsonResponse({"auth_url": meet["auth_url"]})
            
            response = meet.create(summary, start_time, end_time, timezone)
            return JsonResponse({
                "result": response,
                "status": True,
                "message": "Meet created successfully"
            })
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "status": False,
            "message": "Meet creation failed"
        })
    

@csrf_exempt
@require_POST
def create_draft(request: HttpRequest):
    try:
        data = json.loads(request.body)
        message = data.get("message")
        to = data.get("to")
        sender = data.get("sender")
        subject = data.get("subject")
        with Gmail() as gmail:
            response = gmail.create_draft(message, to, sender, subject)
            return JsonResponse({
                "result": response,
                "status": True,
                "message": "Draft created successfully"
            })
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "status": False,
            "message": "Draft creation failed"
        })
    

@csrf_exempt
@require_POST
def create_draft_with_attachment(request: HttpRequest):
    try:
        data = json.loads(request.body)
        message = data.get("message")
        to = data.get("to")
        sender = data.get("sender")
        subject = data.get("subject")
        attachment = data.get("attachment")
        with Gmail() as gmail:
            response = gmail.create_draft_with_attachment(message, to, sender, subject, attachment)
            return JsonResponse({
                "result": response,
                "status": True,
                "message": "Draft created successfully"
            })
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "status": False,
            "message": "Draft creation failed"
        })
    

@csrf_exempt
@require_POST
def send_message(request: HttpRequest):
    try:
        data = json.loads(request.body)
        message = data.get("message")
        to = data.get("to")
        sender = data.get("sender")
        subject = data.get("subject")
        with Gmail() as gmail:
            response = gmail.send_send_message(message, to, sender, subject)
            return JsonResponse({
                "result": response,
                "status": True,
                "message": "Message sent successfully"
            })
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "status": False,
            "message": "Message send failed"
        })
    

@csrf_exempt
@require_POST
def send_message_with_attachment(request: HttpRequest):
    try:
        data = json.loads(request.body)
        message = data.get("message")
        to = data.get("to")
        sender = data.get("sender")
        subject = data.get("subject")
        attachment = data.get("attachment")
        with Gmail() as gmail:
            response = gmail.send_send_message_with_attachment(message, to, sender, subject, attachment)
            return JsonResponse({
                "result": response,
                "status": True,
                "message": "Message sent successfully"
            })
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "status": False,
            "message": "Message send failed"
        })
    

@csrf_exempt
@require_POST
def send_draft(request: HttpRequest):
    try:
        data = json.loads(request.body)
        draft_id = data.get("draft_id")
        with Gmail() as gmail:
            response = gmail.send_draft(draft_id)
            return JsonResponse({
                "result": response,
                "status": True,
                "message": "Draft sent successfully"
            })
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "status": False,
            "message": "Draft send failed"
        })


@csrf_exempt
@require_POST
def create_doc(request: HttpRequest):
    try:
        data = json.loads(request.body)
        title = data.get("title")
        initial_text = data.get("initial_text")
        with Doc() as doc:
            if isinstance(doc, dict) and "auth_url" in doc:
                return JsonResponse({"auth_url": doc["auth_url"]})
            
            response = doc.create(title, initial_text)
            return JsonResponse({
                "result": response,
                "status": True,
                "message": "Document created successfully"
            })
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "status": False,
            "message": "Document creation failed"
        })


@csrf_exempt
@require_GET
def get_doc(request: HttpRequest, doc_id: str):
    try:
        with Doc() as doc:
            response = doc.get(doc_id)
            return JsonResponse({
                "result": response,
                "status": True,
                "message": "Document retrieved successfully"
            })
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "status": False,
            "message": "Document retrieval failed"
        })
    

@csrf_exempt
@require_POST
def add_content(request: HttpRequest, doc_id: str):
    try:
        data = json.loads(request.body)
        text = data.get("text")
        newlines = data.get("newlines", 1)
        with Doc() as doc:
            response = doc.add_content(doc_id, text, newlines)
            return JsonResponse({
                "result": response,
                "status": True,
                "message": "Content added successfully"
            })
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "status": False,
            "message": "Content addition failed"
        })
    
