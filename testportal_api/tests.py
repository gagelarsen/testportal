import json

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from testportal.models import Suite, TestCase, TestCategory, TestSubcategory


class SuiteTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='api-user', password='password123')
        cls.suite = Suite.objects.create(name='Suite1', active=True)
        cls.category = TestCategory.objects.create(category='API Category')
        cls.subcategory = TestSubcategory.objects.create(subcategory='API Subcategory')
        cls.test_case = TestCase.objects.create(
            name='API Test Case',
            test_case_id='API-1',
            steps='Step 1',
            suite=cls.suite,
            category=cls.category,
            subcategory=cls.subcategory,
            status='active',
            test_type='manual',
        )

    def test_view_suites(self):
        url = reverse('testportal_api:suite_list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_suite(self):
        data = {'name': 'Suite2', 'active': True}
        url = reverse('testportal_api:suite_list')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_suite_requires_authentication(self):
        url = reverse('testportal_api:duplicate_suite', kwargs={'suite_id': self.suite.id})
        response = self.client.post(url, {'new_name': 'Suite1 Copy'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_duplicate_suite_copies_test_cases_when_authenticated(self):
        self.client.login(username='api-user', password='password123')
        url = reverse('testportal_api:duplicate_suite', kwargs={'suite_id': self.suite.id})
        response = self.client.post(url, {'new_name': 'Suite1 Copy'})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Suite.objects.filter(name='Suite1 Copy').exists())
        copied_suite = Suite.objects.get(name='Suite1 Copy')
        self.assertEqual(TestCase.objects.filter(suite=copied_suite).count(), 1)

    def test_delete_test_case_requires_authentication(self):
        url = reverse('testportal_api:delete_test_case', kwargs={'pk': self.test_case.id})
        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_test_case_returns_404_for_missing_case(self):
        self.client.login(username='api-user', password='password123')
        url = reverse('testportal_api:delete_test_case', kwargs={'pk': 999999})
        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_upload_multiple_test_cases_requires_authentication(self):
        payload = {'test_cases': []}
        url = reverse('testportal_api:upload_test_cases')
        response = self.client.post(url, {'json': json.dumps(payload)}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_multiple_test_cases_rejects_non_post(self):
        url = reverse('testportal_api:upload_test_cases')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)