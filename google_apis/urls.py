from django.urls import path
from . import views

urlpatterns = [
    # sheet related urls
    path("sheet/create/", views.create_new_sheet, name="create_new_sheet"),
    path("oauth2_callback/", views.oauth2_callback, name="oauth2_callback"),
    path("sheet/<str:sheet_id>/update_values/", views.update_values, name="update_values"),
    path("sheet/<str:sheet_id>/append_values/", views.append_values, name="append_values"),
    path("sheet/<str:sheet_id>/get_values/", views.get_values, name="get_values"),
    path("sheet/<str:sheet_id>/batch_update/", views.batch_update, name="batch_update"),
    path("sheet/<str:sheet_id>/batch_update_values/", views.batch_update_values, name="batch_update_values"),
    path("sheet/<str:sheet_id>/batch_get_values/", views.batch_get_values, name="batch_get_values"),
    path("sheet/<str:sheet_id>/format/", views.conditional_formatting, name="conditional_formatting"),
    path("sheet/<str:sheet_id>/filter/", views.filter_views, name="filter_views"),

    # meeting related urls
    path("meeting/create/", views.create_meet, name="create_meet"),

    # email related urls
    path("email/create_draft/", views.create_draft, name="create_draft"),
    path("email/create_draft_with_attachment/", views.create_draft_with_attachment, name="create_draft_with_attachment"),
    path("email/send_message/", views.send_message, name="send_message"),
    path("email/send_message_with_attachment/", views.send_message_with_attachment, name="send_message_with_attachment"),
    path("email/send_draft/", views.send_draft, name="send_draft"),

    # docs related urls
    path("docs/create_doc/", views.create_doc, name="create_doc"),
    path("docs/<str:doc_id>/get/", views.get_doc, name="get_doc"),
    path("docs/<str:doc_id>/add_content/", views.add_content, name="add_content"),
]