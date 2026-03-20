from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from testportal.models import Suite, TestCategory, TestSubcategory, TestCase as PortalTestCase, TestPlan, TestResult
from testportal.views.dashboard_view import get_item, format_result


class DashboardAndListViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='dash-user', password='password123')

        cls.suite = Suite.objects.create(name='DashSuite', active=True)
        cls.category = TestCategory.objects.create(category='DashCategory')
        cls.subcategory = TestSubcategory.objects.create(subcategory='DashSubcategory')
        cls.plan = TestPlan.objects.create(name='Plan A', suite=cls.suite)

        cls.test_case = PortalTestCase.objects.create(
            name='Dash Case',
            test_case_id='D-1',
            steps='Step',
            suite=cls.suite,
            category=cls.category,
            subcategory=cls.subcategory,
            test_plan=cls.plan,
            status='active',
            test_type='manual',
        )

        TestResult.objects.create(
            result='pass',
            user=cls.user,
            test_case=cls.test_case,
            result_date=date.today(),
            duration=3.0,
        )

    def test_get_item_filter_returns_value_or_none(self):
        data = {'a': 1}

        self.assertEqual(get_item(data, 'a'), 1)
        self.assertIsNone(get_item(data, 'missing'))

    def test_format_result_filter_formats_status(self):
        self.assertEqual(format_result('under-construction'), 'Under Construction')

    def test_dashboard_view_renders_with_results(self):
        url = reverse('testportal:dashboard_view', kwargs={'name': self.suite.name})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['suite'].id, self.suite.id)
        self.assertTrue(response.context['date_list'])
        self.assertEqual(response.context['number_of_days'], 10)
        self.assertEqual(len(response.context['dashboard_data']), 1)

    def test_dashboard_view_invalid_num_days_falls_back_to_30(self):
        url = reverse('testportal:dashboard_view', kwargs={'name': self.suite.name})

        response = self.client.get(url, {'num_days': 'not-a-number'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['number_of_days'], 30)

    def test_dashboard_view_num_days_is_clamped(self):
        url = reverse('testportal:dashboard_view', kwargs={'name': self.suite.name})

        response = self.client.get(url, {'num_days': 999})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['number_of_days'], 365)

    def test_dashboard_view_missing_suite_returns_404(self):
        url = reverse('testportal:dashboard_view', kwargs={'name': 'missing-suite'})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_test_plan_list_view_renders_plans(self):
        url = reverse('testportal:test_plan_list_view')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Plan A')
