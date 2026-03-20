"""
Tests for model __str__ methods and helper methods not covered elsewhere.
"""
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from testportal.models import (
    BugVerification,
    Tag,
    TestCase as TestCaseModel,
    TestCategory,
    TestPlan,
    TestResult,
    TestSubcategory,
    Suite,
)


class BugVerificationStrTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.subcategory = TestSubcategory.objects.create(subcategory='BV Model SC')
        cls.bv = BugVerification.objects.create(
            bug_id=88888,
            summary='Model str test',
            category=cls.subcategory,
            reported_date=date(2026, 1, 1),
            fixed_date=date(2026, 1, 2),
            verified_date=date(2026, 1, 3),
        )

    def test_bug_verification_str_returns_bug_id(self):
        self.assertEqual(str(self.bv), '88888')


class TagStrTest(TestCase):

    def test_tag_str_returns_tag_value(self):
        tag = Tag.objects.create(tag='my-tag-label')
        self.assertEqual(str(tag), 'my-tag-label')


class TestCaseMethodsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='tc-model-user', password='pw')
        cls.suite = Suite.objects.create(name='ModelSuite', active=True)
        cls.category = TestCategory.objects.create(category='ModelCat')
        cls.subcategory = TestSubcategory.objects.create(subcategory='ModelSC')
        cls.tc = TestCaseModel.objects.create(
            name='Model TC',
            test_case_id='MOD-1',
            steps='Steps',
            suite=cls.suite,
            category=cls.category,
            subcategory=cls.subcategory,
            status='active',
            test_type='manual',
        )

    def test_test_case_str_returns_name_and_suite(self):
        expected = f'Model TC - ({self.suite})'
        self.assertEqual(str(self.tc), expected)

    def test_results_for_n_days_returns_todays_result(self):
        TestResult.objects.create(
            result='pass',
            user=self.user,
            test_case=self.tc,
            result_date=date.today(),
            duration=1.5,
        )
        results = self.tc.results_for_n_days(3)
        self.assertIn(date.today(), results)

    def test_results_for_n_days_returns_empty_when_no_results(self):
        results = self.tc.results_for_n_days(3)
        self.assertIsInstance(results, dict)
        self.assertEqual(len(results), 0)


class TestPlanStrTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.suite = Suite.objects.create(name='TPStrSuite', active=True)
        cls.tp = TestPlan.objects.create(name='My Plan', suite=cls.suite)

    def test_test_plan_str_returns_name_and_suite(self):
        self.assertEqual(str(self.tp), f'My Plan ({self.suite})')
