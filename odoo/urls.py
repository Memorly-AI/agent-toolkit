from django.urls import path
from . import views

urlpatterns = [
    path("crm/create_lead/", views.create_lead),
]