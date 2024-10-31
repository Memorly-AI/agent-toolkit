from django.test import TestCase, Client

class TestSetup(TestCase):

    def setUp(self):
        self.client = Client()
        self.BASE_URL = "https://cp.apidev.memorly.ai"
        self.account_id = "4"

