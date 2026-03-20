"""
Extended tests for suite_detail_view covering branches that require test cases with results:
- if test_case_ids block (results query loop)
- average_time calculation when pass results with duration exist
"""
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from testportal.models import (
    Suite,
    TestCase as TestCaseModel,
    TestCategory,
    TestResult,
    TestSubcategory,
)


class SuiteDetailViewWithResultsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='suite-detail-ext-user', password='password123')
        cls.suite = Suite.objects.create(name='DetailExtSuite', active=True)
        cls.category = TestCategory.objects.create(category='DetailExtCat')
        cls.subcategory = TestSubcategory.objects.create(subcategory='DetailExtSC')
        cls.tc = TestCaseModel.objects.create(
            name='Detail Ext TC',
            test_case_id='DE-1',
            steps='Run it',
            suite=cls.suite,
            category=cls.category,
            subcategory=cls.subcategory,
            status='active',
            test_type='manual',
        )
        # Create a pass result with a duration so average_time is computed
        cls.result = TestResult.objects.create(
            result='pass',
            user=cls.user,
            test_case=cls.tc,
            result_date=date(2026, 3, 1),
            duration=5.0,
        )

    def test_suite_detail_view_with_results_renders_200(self):
        url = reverse('testportal:suite_detail_view', kwargs={'name': self.suite.name})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_suite_detail_view_context_has_test_cases_with_results(self):
        url = reverse('testportal:suite_detail_view', kwargs={'name': self.suite.name})
        response = self.client.get(url)

        test_cases = response.context['test_cases']
        self.assertEqual(len(test_cases), 1)
        entry = test_cases[0]
        # The result should be populated (not None)
        self.assertIsNotNone(entry['result'])
        # Average time should reflect the pass result duration
        self.assertAlmostEqual(entry['duration'], 5.0)

    def test_suite_detail_view_multiple_results_averages_duration(self):
        # Create a second pass result with a different duration
        TestResult.objects.create(
            result='pass',
            user=self.user,
            test_case=self.tc,
            result_date=date(2026, 3, 2),
            duration=3.0,
        )
        url = reverse('testportal:suite_detail_view', kwargs={'name': self.suite.name})
        response = self.client.get(url)

        test_cases = response.context['test_cases']
        entry = test_cases[0]
        # Two pass results: durations 5.0 and 3.0 → average 4.0
        self.assertAlmostEqual(entry['duration'], 4.0)

    def test_suite_detail_view_fail_result_excluded_from_avg_duration(self):
        # Only a fail result — duration should be 0 (no pass results)
        suite2 = Suite.objects.create(name='DetailNoDurationSuite', active=True)
        tc2 = TestCaseModel.objects.create(
            name='No Duration TC',
            test_case_id='ND-1',
            steps='Steps',
            suite=suite2,
            category=self.category,
            subcategory=self.subcategory,
            status='active',
            test_type='manual',
        )
        TestResult.objects.create(
            result='fail',
            user=self.user,
            test_case=tc2,
            result_date=date(2026, 3, 1),
            duration=7.0,
        )
        url = reverse('testportal:suite_detail_view', kwargs={'name': 'DetailNoDurationSuite'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        test_cases = response.context['test_cases']
        entry = test_cases[0]
        self.assertEqual(entry['duration'], 0)
