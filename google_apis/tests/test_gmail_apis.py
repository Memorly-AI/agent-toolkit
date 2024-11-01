from django.urls import reverse
from django.test import Client
from google_apis.tests.test_setup import TestSetup
import json


class GmailAPITests(TestSetup):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.draft_id = cls.create_draft()

    @classmethod
    def create_draft(cls):
        url = reverse('create_draft')
        data = {
            "message": "Hello, this is a test message",
            "to": "am.21u10052@btech.nitdgp.ac.in",
            "sender": "misarofazad@gmail.com",
            "subject": "Test message"
        }
        response = cls.client.post(url, json.dumps(data), content_type='application/json')
        assert response.status_code == 200
        response = response.json()
        assert response['status'] == True
        assert response['message'] == 'Draft created successfully'
        return response['result']['id']

    def test_create_draft_with_attachment(self):
        url = reverse('create_draft_with_attachment')
        data = {
            "message": "Hello, this is a test message",
            "to": "am.21u10052@btech.nitdgp.ac.in",
            "sender": "misarofazad@gmail.com",
            "subject": "Test message",
            "attachment": "https://static.googleusercontent.com/media/www.google.com/en//googleblogs/pdfs/google_introduction.pdf"
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertTrue(response['result'])
        self.assertTrue(response['status'])
        self.assertEqual(response['message'], 'Draft created successfully')
        self.draft_id = response['result']['id']

    def test_send_message(self):
        url = reverse('send_message')
        data = {
            "message": "Hello, this is a test message",
            "to": "am.21u10052@btech.nitdgp.ac.in",
            "sender": "misarofazad@gmail.com",
            "subject": "Test message"
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertTrue(response['result'])
        self.assertTrue(response['status'])
        self.assertEqual(response['message'], 'Message sent successfully')

    def test_send_message_with_attachment(self):
        url = reverse('send_message_with_attachment')
        data = {
            "message": "Hello, this is a test message",
            "to": "am.21u10052@btech.nitdgp.ac.in",
            "sender": "misarofazad@gmail.com",
            "subject": "Test message",
            "attachment": "https://static.googleusercontent.com/media/www.google.com/en//googleblogs/pdfs/google_introduction.pdf"
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertTrue(response['result'])
        self.assertTrue(response['status'])
        self.assertEqual(response['message'], 'Message sent successfully')

    def test_send_draft(self):
        url = reverse('send_draft')
        data = {
            "draft_id": self.draft_id
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertTrue(response['status'])
        self.assertEqual(response['message'], 'Draft sent successfully')
