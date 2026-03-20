from datetime import date

from django.test import TestCase
from django.urls import reverse

from testportal.models import BugVerification, Product, Suite, TestSubcategory


class BugVerificationViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.suite = Suite.objects.create(name='BugSuite', active=True)
        cls.product = Product.objects.create(name='ProdA', version='1.0')
        cls.subcategory = TestSubcategory.objects.create(subcategory='Regression')
        cls.verification = BugVerification.objects.create(
            bug_id=1001,
            summary='Fix login crash',
            category=cls.subcategory,
            fixed_date=date(2026, 3, 15),
            reported_date=date(2026, 3, 10),
            verified_date=date(2026, 3, 16),
            test='gui',
        )
        cls.verification.products.add(cls.product)

    def test_general_view_renders_and_shows_verification(self):
        url = reverse('testportal:bug_verifications_general_view')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fix login crash')

    def test_general_view_invalid_dates_populates_errors(self):
        url = reverse('testportal:bug_verifications_general_view')

        response = self.client.get(url, {'start_day': 'bad-date', 'end_day': 'also-bad'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['errors'])

    def test_general_view_filters_by_product(self):
        url = reverse('testportal:bug_verifications_general_view')

        response = self.client.get(url, {'product': 'ProdA-1.0'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_product'].id, self.product.id)
        self.assertEqual(response.context['bug_verifications'].count(), 1)

    def test_general_view_invalid_product_format_adds_error(self):
        url = reverse('testportal:bug_verifications_general_view')

        response = self.client.get(url, {'product': 'invalid'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid product specified: invalid', response.context['errors'])

    def test_general_view_filters_by_category(self):
        url = reverse('testportal:bug_verifications_general_view')

        response = self.client.get(url, {'category': self.subcategory.subcategory})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_category'].id, self.subcategory.id)
        self.assertEqual(response.context['bug_verifications'].count(), 1)

    def test_report_view_groups_verifications_for_existing_product(self):
        url = reverse(
            'testportal:bug_verification_report',
            kwargs={'name': self.product.name, 'version': self.product.version},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['product'].id, self.product.id)
        self.assertIn(self.subcategory, response.context['verifications'])
        self.assertEqual(len(response.context['verifications'][self.subcategory]), 1)

    def test_report_view_missing_product_sets_error(self):
        url = reverse('testportal:bug_verification_report', kwargs={'name': 'Missing', 'version': '9.9'})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['product'])
        self.assertTrue(response.context['errors'])
        self.assertEqual(response.context['verifications'], {})
