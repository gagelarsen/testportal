import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from testportal.models import Suite, TestCategory, TestSubcategory, TestCase


class TestCaseViewFunctionTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='case-user', password='password123')

        cls.suite = Suite.objects.create(name='CaseSuite', active=True)
        cls.category = TestCategory.objects.create(category='CaseCategory')
        cls.subcategory = TestSubcategory.objects.create(subcategory='CaseSubcategory')

    def _valid_case_payload(self):
        return {
            'name': 'Uploaded Case',
            'test_case_id': 'UP-1',
            'steps': 'Step A',
            'status': 'active',
            'suite': self.suite.name,
            'test_type': 'manual',
            'category': self.category.category,
            'subcategory': self.subcategory.subcategory,
        }

    def test_upload_multiple_test_cases_missing_json_field_returns_400(self):
        self.client.login(username='case-user', password='password123')
        url = reverse('testportal_api:upload_test_cases')

        response = self.client.post(url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_multiple_test_cases_invalid_json_returns_400(self):
        self.client.login(username='case-user', password='password123')
        url = reverse('testportal_api:upload_test_cases')

        response = self.client.post(url, {'json': '{invalid'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_multiple_test_cases_non_dict_payload_returns_400(self):
        self.client.login(username='case-user', password='password123')
        url = reverse('testportal_api:upload_test_cases')

        response = self.client.post(url, {'json': json.dumps(['not-a-dict'])})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_multiple_test_cases_non_list_test_cases_returns_400(self):
        self.client.login(username='case-user', password='password123')
        url = reverse('testportal_api:upload_test_cases')

        response = self.client.post(url, {'json': json.dumps({'test_cases': 'not-a-list'})})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_multiple_test_cases_empty_list_returns_400(self):
        self.client.login(username='case-user', password='password123')
        url = reverse('testportal_api:upload_test_cases')

        response = self.client.post(url, {'json': json.dumps({'test_cases': []})})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_multiple_test_cases_invalid_case_object_returns_400(self):
        self.client.login(username='case-user', password='password123')
        url = reverse('testportal_api:upload_test_cases')

        response = self.client.post(url, {'json': json.dumps({'test_cases': ['not-an-object']})})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_multiple_test_cases_missing_required_fields_returns_400(self):
        self.client.login(username='case-user', password='password123')
        url = reverse('testportal_api:upload_test_cases')
        payload = {'test_cases': [{'name': 'Only Name'}]}

        response = self.client.post(url, {'json': json.dumps(payload)})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_multiple_test_cases_unknown_suite_returns_400(self):
        self.client.login(username='case-user', password='password123')
        url = reverse('testportal_api:upload_test_cases')
        case = self._valid_case_payload()
        case['suite'] = 'MissingSuite'

        response = self.client.post(url, {'json': json.dumps({'test_cases': [case]})})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_multiple_test_cases_unknown_category_returns_400(self):
        self.client.login(username='case-user', password='password123')
        url = reverse('testportal_api:upload_test_cases')
        case = self._valid_case_payload()
        case['category'] = 'MissingCategory'

        response = self.client.post(url, {'json': json.dumps({'test_cases': [case]})})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_multiple_test_cases_unknown_subcategory_returns_400(self):
        self.client.login(username='case-user', password='password123')
        url = reverse('testportal_api:upload_test_cases')
        case = self._valid_case_payload()
        case['subcategory'] = 'MissingSubcategory'

        response = self.client.post(url, {'json': json.dumps({'test_cases': [case]})})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_multiple_test_cases_success_returns_instances(self):
        self.client.login(username='case-user', password='password123')
        url = reverse('testportal_api:upload_test_cases')
        payload = {'test_cases': [self._valid_case_payload()]}

        response = self.client.post(url, {'json': json.dumps(payload)})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('instances', response.json())
        self.assertEqual(TestCase.objects.filter(name='Uploaded Case').count(), 1)

    def test_upload_multiple_test_cases_duplicate_conflict_returns_409(self):
        TestCase.objects.create(
            name='Existing Case',
            test_case_id='UP-1',
            steps='Existing',
            suite=self.suite,
            category=self.category,
            subcategory=self.subcategory,
            status='active',
            test_type='manual',
        )
        self.client.login(username='case-user', password='password123')
        url = reverse('testportal_api:upload_test_cases')
        payload = {'test_cases': [self._valid_case_payload()]}

        response = self.client.post(url, {'json': json.dumps(payload)})

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_upload_multiple_test_cases_database_error_returns_400(self):
        self.client.login(username='case-user', password='password123')
        url = reverse('testportal_api:upload_test_cases')
        payload = {'test_cases': [self._valid_case_payload()]}

        with patch('testportal_api.views.test_case_views.TestCase.objects.bulk_create', side_effect=DatabaseError('db down')):
            response = self.client.post(url, {'json': json.dumps(payload)})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_test_case_rejects_invalid_method(self):
        self.client.login(username='case-user', password='password123')
        case = TestCase.objects.create(
            name='Delete Case',
            test_case_id='DEL-1',
            steps='Delete me',
            suite=self.suite,
            category=self.category,
            subcategory=self.subcategory,
            status='active',
            test_type='manual',
        )
        url = reverse('testportal_api:delete_test_case', kwargs={'pk': case.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_test_case_success_for_authenticated_user(self):
        self.client.login(username='case-user', password='password123')
        case = TestCase.objects.create(
            name='Delete Case 2',
            test_case_id='DEL-2',
            steps='Delete me too',
            suite=self.suite,
            category=self.category,
            subcategory=self.subcategory,
            status='active',
            test_type='manual',
        )
        url = reverse('testportal_api:delete_test_case', kwargs={'pk': case.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(TestCase.objects.filter(id=case.id).exists())

    def test_delete_test_case_database_error_returns_400(self):
        self.client.login(username='case-user', password='password123')
        case = TestCase.objects.create(
            name='Delete Case 3',
            test_case_id='DEL-3',
            steps='Delete maybe',
            suite=self.suite,
            category=self.category,
            subcategory=self.subcategory,
            status='active',
            test_type='manual',
        )
        url = reverse('testportal_api:delete_test_case', kwargs={'pk': case.id})

        with patch('testportal_api.views.test_case_views.TestCase.delete', side_effect=DatabaseError('cannot delete')):
            response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
