from django.test import TestCase, Client
from utils.constants import get_env_variable

class TestSetup(TestCase):

    def setUp(self):
        self.client = Client()
        self.BASE_URL = get_env_variable("BASE_URL")

