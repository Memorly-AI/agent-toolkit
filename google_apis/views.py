from google_apis.util.Auth import Auth
from google_apis.util.Doc import Doc
from django.http import JsonResponse
from django.http.request import HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import json
from urllib.parse import parse_qs


@csrf_exempt
@require_GET
def oauth2_callback(request: HttpRequest):
    try:
        state = request.GET.get('state')
        if state:
            state_data = parse_qs(state)
            uid = state_data.get('uid', [None])[0]  
            apps = state_data.get('apps', [None])[0] 
        else:
            return JsonResponse({"error": "State parameter not provided"}, status=400)
        
        if not uid:
            return JsonResponse({"error": "user_id not provided in the callback URL"}, status=400)
        
        code = request.GET.get("code", None)
        if not code:
            return JsonResponse({"error": "Authorization code not provided"}, status=400)
        
        apps = apps.split(",") if apps else []
        auth = Auth(uid, apps=apps)
        response = auth.authorize(code)

        return JsonResponse({"response": response})
    except Exception as e:
        return JsonResponse({"error": str(e)})
    

def get_auth_url(uid: str, apps: list = ['all']):
    try:
        auth = Auth(uid, apps=apps)
        is_authorized = auth.check_auth()
        if is_authorized:
            return "Already authorized", True
        response = auth.get_auth_url()
        return response, False
    except Exception as e:
        return str(e), False


@csrf_exempt
@require_POST
def create_auth_url(request: HttpRequest):
    """
        Create an authorization URL for Google API.
        
        Request Parameters:
        - `tool_id` (str): Unique identifier for authentication (required)
        - `apps` (list): List of apps to authorize (optional)
        
        Response: Returns the authorization URL or an error message

        # call this api url like this with apps
        api_url = "/api/v1/google_apis/create_auth_url?apps=drive,docs,sheet,gmail"
    """
    try:
        apps = request.GET.get("apps", ['all']).strip().lower().replace(" ", "").split(",")
        data = json.loads(request.body)
        uid = data.get("tool_id", None)
        
        if not uid: 
            return JsonResponse({"error": "The owner is not found"}, status=400)
        
        response, status = get_auth_url(uid, apps)
        return JsonResponse({
            "auth_url": response,
            "authorized": status
        }, status=200)  
    except Exception as e:
        return JsonResponse({"error": str(e)})
     

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
    
