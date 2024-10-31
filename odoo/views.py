from django.shortcuts import render
from odoo.crm.crm import CRM
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import json


@csrf_exempt
@require_POST
def create_lead(request):
    try:
        data = json.loads(request.body)
        name = data.get("name")
        phone = data.get("phone")
        org_url = data.get("org_url")
        db = data.get("db")
        key = data.get("key")
        user_name = data.get("user_name")
        crm = CRM(org_url, db, key, user_name)
        response = crm.create_lead(name, phone)
        return JsonResponse({"response": response})
    except Exception as e:
        return JsonResponse({"error": str(e)})
