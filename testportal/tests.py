from django.test import TestCase
from django.urls import reverse

from datetime import date

from django.contrib.auth import get_user_model

from testportal.models import Suite, TestCategory, TestSubcategory, TestCase as PortalTestCase, TestResult


class TestCreateSuite(TestCase):

    @classmethod
    def setUpTestData(cls):
        Suite.objects.create(name='Test1', active=True)

    def test_suite_content(self):
        suite = Suite.objects.get(id=1)

        self.assertEqual(suite.name, 'Test1')
        self.assertTrue(suite.active)

        self.assertEqual(str(suite), 'Test1')


class TestCaseModelMethods(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='tester', password='password123')
        cls.suite = Suite.objects.create(name='ModelSuite', active=True)
        cls.category = TestCategory.objects.create(category='Regression')
        cls.subcategory = TestSubcategory.objects.create(subcategory='Smoke')
        cls.test_case = PortalTestCase.objects.create(
            name='Login Works',
            test_case_id='TC-100',
            steps='1. Open app\n2. Login',
            suite=cls.suite,
            category=cls.category,
            subcategory=cls.subcategory,
            status='active',
            test_type='manual',
        )
        cls.result_1 = TestResult.objects.create(
            result='pass',
            user=cls.user,
            test_case=cls.test_case,
            result_date=date(2026, 3, 10),
            duration=12.0,
        )
        cls.result_2 = TestResult.objects.create(
            result='fail',
            user=cls.user,
            test_case=cls.test_case,
            result_date=date(2026, 3, 11),
            duration=10.0,
        )

    def test_results_for_dates_returns_expected_mapping(self):
        selected_dates = [date(2026, 3, 10), date(2026, 3, 11), date(2026, 3, 12)]
        results = self.test_case.results_for_dates(selected_dates)

        self.assertEqual(set(results.keys()), {date(2026, 3, 10), date(2026, 3, 11)})
        self.assertEqual(results[date(2026, 3, 10)].id, self.result_1.id)
        self.assertEqual(results[date(2026, 3, 11)].id, self.result_2.id)

    def test_get_last_result_returns_most_recent_result(self):
        last_result = self.test_case.get_last_result()

        self.assertIsNotNone(last_result)
        self.assertEqual(last_result.id, self.result_2.id)


class WebViewSmokeTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.suite = Suite.objects.create(name='WebSuite', active=True)

    def test_suite_list_view_renders(self):
        response = self.client.get(reverse('testportal:suite_list_view'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'WebSuite')

    def test_suite_detail_view_renders_for_existing_suite(self):
        response = self.client.get(reverse('testportal:suite_detail_view', kwargs={'name': self.suite.name}))

        self.assertEqual(response.status_code, 200)

    def test_suite_detail_view_404_for_missing_suite(self):
        response = self.client.get(reverse('testportal:suite_detail_view', kwargs={'name': 'missing-suite'}))

        self.assertEqual(response.status_code, 404)