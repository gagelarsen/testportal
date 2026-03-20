"""
Tests for suite_views.py covering all branches of duplicate_suite:
- GET → 405
- Empty name → 400
- Non-existent suite → 404
- Existing name conflict → 400
- IntegrityError mock → 409
- DatabaseError mock → 400
"""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import DatabaseError, IntegrityError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from testportal.models import Suite


class DuplicateSuiteViewTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='dup-suite-user', password='password123')
        cls.suite = Suite.objects.create(name='OriginalSuiteForDup', active=True)

    def test_get_returns_405(self):
        """Line 22: non-POST method returns 405."""
        url = reverse('testportal_api:duplicate_suite', kwargs={'suite_id': self.suite.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_with_empty_name_returns_400(self):
        """Line 30: empty/blank new_name returns 400."""
        self.client.login(username='dup-suite-user', password='password123')
        url = reverse('testportal_api:duplicate_suite', kwargs={'suite_id': self.suite.id})
        response = self.client.post(url, {'new_name': '   '})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_with_missing_name_returns_400(self):
        """Line 30: missing new_name returns 400."""
        self.client.login(username='dup-suite-user', password='password123')
        url = reverse('testportal_api:duplicate_suite', kwargs={'suite_id': self.suite.id})
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_with_nonexistent_suite_returns_404(self):
        """Lines 34-35: Suite.DoesNotExist → 404."""
        self.client.login(username='dup-suite-user', password='password123')
        url = reverse('testportal_api:duplicate_suite', kwargs={'suite_id': 999999})
        response = self.client.post(url, {'new_name': 'SomeNewName'})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_with_existing_name_returns_400(self):
        """Line 38: Suite with new_name already exists → 400."""
        self.client.login(username='dup-suite-user', password='password123')
        url = reverse('testportal_api:duplicate_suite', kwargs={'suite_id': self.suite.id})
        response = self.client.post(url, {'new_name': self.suite.name})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_integrity_error_returns_409(self):
        """Lines 65-67: IntegrityError during transaction → 409."""
        self.client.login(username='dup-suite-user', password='password123')
        url = reverse('testportal_api:duplicate_suite', kwargs={'suite_id': self.suite.id})
        with patch('testportal_api.views.suite_views.Suite.objects.create',
                   side_effect=IntegrityError('duplicate')):
            response = self.client.post(url, {'new_name': 'IntegrityErrorSuite'})

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_post_database_error_returns_400(self):
        """Lines 68-70: DatabaseError during transaction → 400."""
        self.client.login(username='dup-suite-user', password='password123')
        url = reverse('testportal_api:duplicate_suite', kwargs={'suite_id': self.suite.id})
        with patch('testportal_api.views.suite_views.Suite.objects.create',
                   side_effect=DatabaseError('db error')):
            response = self.client.post(url, {'new_name': 'DatabaseErrorSuite'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
