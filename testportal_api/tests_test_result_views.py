from datetime import date

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from testportal.models import Suite, TestCase, TestCategory, TestSubcategory, TestResult


class TestResultViewFunctionTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='result-user', password='password123')
        cls.suite = Suite.objects.create(name='ResultSuite', active=True)
        cls.category = TestCategory.objects.create(category='ResultCategory')
        cls.subcategory = TestSubcategory.objects.create(subcategory='ResultSubcategory')
        cls.test_case = TestCase.objects.create(
            name='Result Test Case',
            test_case_id='RES-1',
            steps='Run steps',
            suite=cls.suite,
            category=cls.category,
            subcategory=cls.subcategory,
            status='active',
            test_type='manual',
        )

    def _build_results_xml(self, test_name='Result Test Case', status='0', duration='2000'):
        xml_text = f"""
<Root>
  <A>
    <B>
      <Node name="project">
        <Node name="tests">
          <Node>
            <Prp name="name" value="{test_name}" />
            <Prp name="status" value="{status}" />
            <Prp name="duration" value="{duration}" />
          </Node>
        </Node>
      </Node>
    </B>
  </A>
</Root>
""".strip()
        return xml_text.encode('utf-8')

    def test_delete_test_results_missing_suite_returns_404(self):
        url = reverse(
            'testportal_api:delete_test_results_for_date_and_suite',
            kwargs={'suite': 'MissingSuite', 'month': 3, 'day': 20, 'year': 2026},
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_test_results_bad_date_returns_400(self):
        url = reverse(
            'testportal_api:delete_test_results_for_date_and_suite',
            kwargs={'suite': self.suite.name, 'month': 99, 'day': 20, 'year': 2026},
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_test_results_non_post_returns_405(self):
        url = reverse('testportal_api:upload_test_results', kwargs={'pk': self.suite.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_upload_test_results_requires_authentication(self):
        url = reverse('testportal_api:upload_test_results', kwargs={'pk': self.suite.id})

        response = self.client.post(url, {'upload-results-date': '2026-03-20'})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_test_results_invalid_xml_returns_400(self):
        self.client.login(username='result-user', password='password123')
        url = reverse('testportal_api:upload_test_results', kwargs={'pk': self.suite.id})
        bad_file = SimpleUploadedFile('bad.xml', b'not xml', content_type='text/xml')

        response = self.client.post(
            url,
            {'upload-results-date': '2026-03-20', 'results_file': bad_file},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_test_results_success_creates_result(self):
        self.client.login(username='result-user', password='password123')
        url = reverse('testportal_api:upload_test_results', kwargs={'pk': self.suite.id})
        good_file = SimpleUploadedFile('results.xml', self._build_results_xml(), content_type='text/xml')

        response = self.client.post(
            url,
            {'upload-results-date': '2026-03-20', 'results_file': good_file},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TestResult.objects.filter(test_case=self.test_case).count(), 1)

    def test_upload_test_results_conflict_returns_409(self):
        TestResult.objects.create(
            result='pass',
            user=self.user,
            test_case=self.test_case,
            result_date=date(2026, 3, 20),
            duration=2.0,
        )
        self.client.login(username='result-user', password='password123')
        url = reverse('testportal_api:upload_test_results', kwargs={'pk': self.suite.id})
        good_file = SimpleUploadedFile('results.xml', self._build_results_xml(), content_type='text/xml')

        response = self.client.post(
            url,
            {'upload-results-date': '2026-03-20', 'results_file': good_file},
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_copy_result_to_latest_requires_authentication(self):
        result = TestResult.objects.create(
            result='pass',
            user=self.user,
            test_case=self.test_case,
            result_date=date(2026, 3, 21),
            duration=3.0,
        )
        url = reverse('testportal_api:copy_result_to_latest', kwargs={'result_id': result.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_copy_result_to_latest_returns_418_for_latest_result(self):
        self.client.login(username='result-user', password='password123')
        latest = TestResult.objects.create(
            result='pass',
            user=self.user,
            test_case=self.test_case,
            result_date=date(2026, 3, 22),
            duration=4.0,
        )
        url = reverse('testportal_api:copy_result_to_latest', kwargs={'result_id': latest.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 418)

    def test_copy_result_to_latest_copies_fields(self):
        self.client.login(username='result-user', password='password123')
        source = TestResult.objects.create(
            result='fail',
            note='Copied note',
            bug_id='1234',
            user=self.user,
            test_case=self.test_case,
            result_date=date(2026, 3, 20),
            duration=9.0,
        )
        latest = TestResult.objects.create(
            result='pass',
            note='Latest note',
            user=self.user,
            test_case=self.test_case,
            result_date=date(2026, 3, 21),
            duration=1.0,
        )
        url = reverse('testportal_api:copy_result_to_latest', kwargs={'result_id': source.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        latest.refresh_from_db()
        self.assertEqual(latest.result, source.result)
        self.assertEqual(latest.bug_id, source.bug_id)
        self.assertEqual(latest.note, 'Copied note(Copied)')
