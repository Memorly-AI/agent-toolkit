from django.urls import reverse
from django.test import Client
from google_apis.tests.test_setup import TestSetup
import json


class SheetAPITests(TestSetup):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.sheet_id = cls.create_new_sheet()

    @classmethod
    def create_new_sheet(cls):
        url = reverse('create_new_sheet')
        title = 'Sheet1'
        response = cls.client.post(url, json.dumps({'title': title}), content_type='application/json')
        assert response.status_code == 200
        response = response.json()
        assert response['message'] == 'Sheet created successfully'
        assert response['status'] == True
        return response['result']

    def test_update_values(self):
        url = reverse('update_values', args=[self.sheet_id])
        data = {
            "range_name": "A1:C2",
            "value_input_option": "USER_ENTERED",
            "values": [["10", "15"], ["20", "25"]]
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response['message'], 'Values updated successfully')
        self.assertEqual(response['status'], True)
        self.append_values()

    def append_values(self):
        url = reverse('append_values', args=[self.sheet_id])
        data = {
            "range_name": "A1:C2",
            "value_input_option": "USER_ENTERED",
            "values": [["40", "45"], ["50", "55"]]
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response['message'], 'Values appended successfully')
        self.assertEqual(response['status'], True)

    def test_get_values(self):
        url = reverse('get_values', args=[self.sheet_id])
        data = {
            "range_name": "A1:C2"
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response['message'], 'Values retrieved successfully')
        self.assertEqual(response['status'], True)

    def test_batch_update(self):
        url = reverse('batch_update', args=[self.sheet_id])
        data = {
            "title": "mysheet2",
            "find": "10",
            "replacement": "100"
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response['message'], 'Values updated successfully')
        self.assertEqual(response['status'], True)
        self.batch_get_values()

    def batch_get_values(self):
        url = reverse('batch_get_values', args=[self.sheet_id])
        data = {
            "range_names": ["A1:C2", "D1:E2"]
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response['message'], 'Values retrieved successfully')
        self.assertEqual(response['status'], True)

    def test_batch_update_values(self):
        url = reverse('batch_update_values', args=[self.sheet_id])
        data = {
            "range_name": "A1:C2",
            "value_input_option": "USER_ENTERED",
            "values": [["F", "B"], ["C", "D"]]
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response['message'], 'Values updated successfully')
        self.assertEqual(response['status'], True)

    def test_conditional_formatting(self):
        url = reverse('conditional_formatting', args=[self.sheet_id])
        data = {
            "format": [
                {
                    "addConditionalFormatRule": {
                        "rule": {
                            "ranges": [
                                {
                                    "sheetId": 0,
                                    "startRowIndex": 1,
                                    "endRowIndex": 11,
                                    "startColumnIndex": 0,
                                    "endColumnIndex": 4,
                                }
                            ],
                            "booleanRule": {
                                "condition": {
                                    "type": "CUSTOM_FORMULA",
                                    "values": [
                                        {
                                            "userEnteredValue": "=GT($D2,median($D$2:$D$11))"
                                        }
                                    ]
                                },
                                "format": {
                                    "textFormat": {
                                        "foregroundColor": {
                                            "red": 0.8
                                        }
                                    }
                                }
                            }
                        },
                        "index": 0
                    }
                },
                {
                    "addConditionalFormatRule": {
                        "rule": {
                            "ranges": [
                                {
                                    "sheetId": 0,
                                    "startRowIndex": 1,
                                    "endRowIndex": 11,
                                    "startColumnIndex": 0,
                                    "endColumnIndex": 4,
                                }
                            ],
                            "booleanRule": {
                                "condition": {
                                    "type": "CUSTOM_FORMULA",
                                    "values": [
                                        {
                                            "userEnteredValue": "=LT($D2,median($D$2:$D$11))"
                                        }
                                    ]
                                },
                                "format": {
                                    "backgroundColor": {
                                        "red": 1,
                                        "green": 0.4,
                                        "blue": 0.4
                                    }
                                }
                            }
                        },
                        "index": 0
                    }
                }
            ]
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response['message'], 'Conditional formatting applied successfully')
        self.assertEqual(response['status'], True)

    def test_filter_views(self):
        url = reverse('filter_views', args=[self.sheet_id])
        data = {
            "range": {
                "sheetId": 0,
                "startRowIndex": 0,
                "startColumnIndex": 0
            }
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response['message'], 'Filter views applied successfully')
        self.assertEqual(response['status'], True)
