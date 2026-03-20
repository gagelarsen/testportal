"""
Extended bug_verifications view tests covering the "found" paths for product and category filters
(lines 49-50 and 59-60 in bug_verifications.py).
"""
from django.test import TestCase
from django.urls import reverse

from testportal.models import Product, TestSubcategory


class BugVerificationFoundPathsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.subcategory = TestSubcategory.objects.create(subcategory='BVExtSC')
        cls.product = Product.objects.create(name='BVExtProd', version='2.0')

    def test_general_view_product_regex_match_but_not_in_db_adds_error(self):
        """Lines 49-50: format matches regex but no product in DB → DoesNotExist error."""
        url = reverse('testportal:bug_verifications_general_view')
        response = self.client.get(url, {'product': 'NoSuchProduct-0.0'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('No matching product exists for NoSuchProduct-0.0', response.context['errors'])

    def test_general_view_category_not_in_db_adds_error(self):
        """Lines 59-60: category string provided but TestSubcategory.DoesNotExist → error."""
        url = reverse('testportal:bug_verifications_general_view')
        response = self.client.get(url, {'category': 'NoSuchCategory'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('No matching category exists for NoSuchCategory', response.context['errors'])
