from django.urls import path
from . import views
from .calendar_tool import *
from .sheet_tool import google_sheets_api
from .meet_tool import google_meet_api
from .gmail_tool import gmail_api

urlpatterns = [
    path("auth-url/get/", views.create_auth_url, name="create_auth_url"),
    path("oauth2_callback/", views.oauth2_callback, name="oauth2_callback"),

    path("sheet/", google_sheets_api, name="google_sheets_api"),
    path("calendar/", google_calender_api, name="google_calender_api"),
    path("meet/", google_meet_api, name="google_meets_api"),
    path("gmail/", gmail_api, name="gmail_api"),   

    # docs related urls
    path("docs/create_doc/", views.create_doc, name="create_doc"),
    path("docs/<str:doc_id>/get/", views.get_doc, name="get_doc"),
    path("docs/<str:doc_id>/add_content/", views.add_content, name="add_content"), 
]