from django.urls import reverse
from django.test import Client
from google_apis.tests.test_setup import TestSetup
import json


class DocsAPITests(TestSetup):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.doc_id = cls.create_doc()

    @classmethod
    def create_doc(cls):
        url = reverse('create_doc')
        data = {
            "title": "Test Document",
            "initial_text": "This is a test document"
        }
        response = cls.client.post(url, json.dumps(data), content_type='application/json')
        assert response.status_code == 200
        response = response.json()
        assert response['status']
        assert response['message'] == 'Document created successfully'
        return response['result']

    def test_get_doc(self):
        url = reverse('get_doc', args=[self.doc_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertTrue(response['result'])
        self.assertTrue(response['status'])
        self.assertEqual(response['message'], 'Document retrieved successfully')

    def test_add_content(self):
        url = reverse('add_content', args=[self.doc_id])
        data = {
            "text": "This is a new line",
            "newlines": 2
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertTrue(response['result'])
        self.assertTrue(response['status'])
        self.assertEqual(response['message'], 'Content added successfully')
        