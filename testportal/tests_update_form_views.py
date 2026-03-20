"""
Tests for the shared FormContextMixin used in all Update/Create form views.
Each test exercises get_context_data (via GET) and get_success_url (via POST).
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from testportal.models import (
    BugVerification,
    Product,
    Suite,
    TestCase as TestCaseModel,
    TestCategory,
    TestPlan,
    TestResult,
    TestSubcategory,
)


class BugVerificationFormViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='bv-form-user', password='password123')
        cls.subcategory = TestSubcategory.objects.create(subcategory='BV Form SC')
        cls.bv = BugVerification.objects.create(
            bug_id=77770,
            summary='Form view test BV',
            category=cls.subcategory,
            reported_date='2026-01-01',
            fixed_date='2026-01-02',
            verified_date='2026-01-03',
        )

    def setUp(self):
        self.client.login(username='bv-form-user', password='password123')

    def test_get_context_data_includes_suites_and_referrer(self):
        url = reverse('testportal:bug_verification_update', kwargs={'pk': self.bv.pk})
        response = self.client.get(url, HTTP_REFERER='/from-here/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('suites', response.context)
        self.assertIn('referrer', response.context)

    def test_get_success_url_redirects_to_referrer(self):
        url = reverse('testportal:bug_verification_create')
        data = {
            'bug_id': 77771,
            'summary': 'New BV for redirect test',
            'reported_date': '2026-01-01',
            'fixed_date': '2026-01-02',
            'verified_date': '2026-01-03',
            'category': self.subcategory.pk,
            'test': 'nongui',
            'referrer': '/suites/',
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/suites/')

    def test_get_success_url_defaults_to_slash_when_no_referrer(self):
        url = reverse('testportal:bug_verification_create')
        data = {
            'bug_id': 77772,
            'summary': 'Another BV for default redirect',
            'reported_date': '2026-01-01',
            'fixed_date': '2026-01-02',
            'verified_date': '2026-01-03',
            'category': self.subcategory.pk,
            'test': 'nongui',
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/')


class ProductFormViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='prod-form-user', password='password123')
        cls.product = Product.objects.create(name='FormTestProduct', version='1.0')

    def setUp(self):
        self.client.login(username='prod-form-user', password='password123')

    def test_get_renders_form_with_context(self):
        url = reverse('testportal:product_update', kwargs={'pk': self.product.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('suites', response.context)
        self.assertIn('referrer', response.context)

    def test_post_with_referrer_redirects_to_referrer(self):
        url = reverse('testportal:product_create')
        data = {'name': 'NewFormProd', 'version': '2.0', 'referrer': '/suites/'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/suites/')

    def test_post_without_referrer_redirects_to_slash(self):
        url = reverse('testportal:product_create')
        data = {'name': 'NewFormProd2', 'version': '3.0'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/')


class TestCaseFormViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='tc-form-user', password='password123')
        cls.suite = Suite.objects.create(name='FormSuite', active=True)
        cls.category = TestCategory.objects.create(category='FormCat')
        cls.subcategory = TestSubcategory.objects.create(subcategory='FormSC')
        cls.tc = TestCaseModel.objects.create(
            name='Form TC',
            test_case_id='FORM-1',
            steps='Steps here',
            suite=cls.suite,
            category=cls.category,
            subcategory=cls.subcategory,
            status='active',
            test_type='manual',
        )

    def setUp(self):
        self.client.login(username='tc-form-user', password='password123')

    def test_get_renders_form_with_context(self):
        url = reverse('testportal:test_case_update_view', kwargs={'pk': self.tc.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('suites', response.context)
        self.assertIn('referrer', response.context)

    def test_post_with_referrer_redirects_to_referrer(self):
        url = reverse('testportal:test_case_create_view')
        data = {
            'name': 'Created Form TC',
            'test_case_id': 'FORM-2',
            'steps': 'Step 1\nStep 2',
            'suite': self.suite.pk,
            'category': self.category.pk,
            'subcategory': self.subcategory.pk,
            'status': 'active',
            'test_type': 'manual',
            'referrer': '/suites/',
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/suites/')

    def test_post_without_referrer_redirects_to_slash(self):
        url = reverse('testportal:test_case_create_view')
        data = {
            'name': 'Created Form TC 2',
            'test_case_id': 'FORM-3',
            'steps': 'Step A',
            'suite': self.suite.pk,
            'category': self.category.pk,
            'subcategory': self.subcategory.pk,
            'status': 'active',
            'test_type': 'manual',
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/')


class TestPlanFormViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='tp-form-user', password='password123')
        cls.suite = Suite.objects.create(name='TPFormSuite', active=True)
        cls.tp = TestPlan.objects.create(name='Form Plan', suite=cls.suite)

    def setUp(self):
        self.client.login(username='tp-form-user', password='password123')

    def test_get_renders_form_with_context(self):
        url = reverse('testportal:test_plan_update', kwargs={'pk': self.tp.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('suites', response.context)
        self.assertIn('referrer', response.context)

    def test_post_with_referrer_redirects_to_referrer(self):
        url = reverse('testportal:test_plan_create')
        data = {'name': 'Created Form Plan', 'suite': self.suite.pk, 'referrer': '/suites/'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/suites/')

    def test_post_without_referrer_redirects_to_slash(self):
        url = reverse('testportal:test_plan_create')
        data = {'name': 'Created Form Plan 2', 'suite': self.suite.pk}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/')


class TestResultFormViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='tr-form-user', password='password123')
        cls.suite = Suite.objects.create(name='TRFormSuite', active=True)
        cls.category = TestCategory.objects.create(category='TRFormCat')
        cls.subcategory = TestSubcategory.objects.create(subcategory='TRFormSC')
        cls.tc = TestCaseModel.objects.create(
            name='TR Form TC',
            test_case_id='TRF-1',
            steps='Steps',
            suite=cls.suite,
            category=cls.category,
            subcategory=cls.subcategory,
            status='active',
            test_type='manual',
        )
        cls.tr = TestResult.objects.create(
            result='pass',
            user=cls.user,
            test_case=cls.tc,
            result_date='2026-01-01',
            duration=1.0,
        )

    def setUp(self):
        self.client.login(username='tr-form-user', password='password123')

    def test_get_renders_form_with_context(self):
        url = reverse('testportal:test_result_update', kwargs={'pk': self.tr.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('suites', response.context)
        self.assertIn('referrer', response.context)

    def test_post_with_referrer_redirects_to_referrer(self):
        url = reverse('testportal:test_result_create')
        data = {
            'result': 'pass',
            'user': self.user.pk,
            'test_case': self.tc.pk,
            'result_date': '2026-02-01',
            'referrer': '/suites/',
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/suites/')

    def test_post_without_referrer_redirects_to_slash(self):
        url = reverse('testportal:test_result_create')
        data = {
            'result': 'fail',
            'user': self.user.pk,
            'test_case': self.tc.pk,
            'result_date': '2026-03-01',
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/')
