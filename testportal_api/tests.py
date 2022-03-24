from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Suite


class SuiteTests(APITestCase):

    def test_view_suites(self):
        url = reverse('testportal_api:listcreate')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_suite(self):
        data = {'name': 'Suite2', 'active': True}
        url = reverse('testportal_api:listcreate')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)