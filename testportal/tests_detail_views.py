from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from testportal.models import Suite, TestPlan, TestCategory, TestSubcategory, TestCase as PortalTestCase, TestResult


class DetailViewCoverageTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='detail-user', password='password123')

        cls.suite = Suite.objects.create(name='DetailSuite', active=True)
        cls.category = TestCategory.objects.create(category='DetailCategory')
        cls.subcategory = TestSubcategory.objects.create(subcategory='DetailSubcategory')
        cls.plan = TestPlan.objects.create(name='Detail Plan', suite=cls.suite, description='Plan description')

        cls.test_case = PortalTestCase.objects.create(
            name='Detail Case',
            test_case_id='DET-1',
            notes='Some notes',
            steps='Step 1\nStep 2',
            suite=cls.suite,
            category=cls.category,
            subcategory=cls.subcategory,
            test_plan=cls.plan,
            status='active',
            test_type='manual',
        )

        TestResult.objects.create(
            result='pass',
            note='first',
            user=cls.user,
            test_case=cls.test_case,
            result_date=date(2026, 3, 1),
            duration=2.0,
        )
        TestResult.objects.create(
            result='pass',
            note='second',
            user=cls.user,
            test_case=cls.test_case,
            result_date=date(2026, 3, 2),
            duration=4.0,
        )

    def test_test_case_detail_view_renders_context(self):
        url = reverse('testportal:test_case_detail_view', kwargs={'test_case_id': self.test_case.id})

        response = self.client.get(url, HTTP_REFERER='/suites/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['test_case'].id, self.test_case.id)
        self.assertEqual(response.context['referrer'], '/suites/')
        self.assertEqual(response.context['average_test_time'], 3.0)
        self.assertEqual(len(response.context['recent_results']), 2)

    def test_test_case_detail_view_returns_404_for_missing_case(self):
        url = reverse('testportal:test_case_detail_view', kwargs={'test_case_id': 999999})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_test_plan_detail_view_renders_and_aggregates(self):
        url = reverse('testportal:test_plan_detail_view', kwargs={'test_plan_id': self.plan.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['test_plan'].id, self.plan.id)
        self.assertEqual(len(response.context['test_cases']), 1)
        self.assertIn('active', list(response.context['status_counts_keys']))
        self.assertIn('pass', list(response.context['result_counts_keys']))

    def test_test_plan_detail_view_returns_404_for_missing_plan(self):
        url = reverse('testportal:test_plan_detail_view', kwargs={'test_plan_id': 999999})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
