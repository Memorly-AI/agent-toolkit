from django.urls import reverse
from django.test import Client
from google_apis.tests.test_setup import TestSetup
import json


class MeetAPITests(TestSetup):

    def test_create_meet(self):
        url = reverse('create_meet')
        data = {
            "summary": "Meeting with client",
            "start_time": "2024-11-02T09:00:00",
            "end_time": "2024-11-02T10:00:00",
            "timezone": "Asia/Kolkata"
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertTrue(response['result'])
        self.assertTrue(response['status'])
        self.assertEqual(response['message'], 'Meet created successfully')
   