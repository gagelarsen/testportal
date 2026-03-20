"""
Extended tests for test_result_views.py covering all remaining uncovered branches:
- delete_test_results success and DatabaseError paths
- upload_test_results edge cases (no file, multiple files, no date, bad date, suite not found,
  blank test case name, unknown test case, DatabaseError on bulk_create)
- _parse_test_case_info: non-Prp child, invalid numeric duration
- _parse_result_file: project-level Prp elements, None name/value, bad int, duration branches,
  invalid float duration, no tests node
- copy_result_to_latest: result not found, latest_result is None (dead branch via mock),
  DatabaseError on save
"""
from datetime import date
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import DatabaseError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from testportal.models import Suite, TestCase, TestCategory, TestResult, TestSubcategory


def _xml(body_xml):
    """Wrap body XML inside the standard file structure."""
    return f"""
<Root>
  <A>
    <B>
      <Node name="project">
        {body_xml}
      </Node>
    </B>
  </A>
</Root>
""".strip().encode('utf-8')


def _tests_node(cases_xml):
    return f'<Node name="tests">{cases_xml}</Node>'


def _case_node(name='TC', status='0', duration='1000', extra=''):
    return f'<Node><Prp name="name" value="{name}" /><Prp name="status" value="{status}" /><Prp name="duration" value="{duration}" />{extra}</Node>'


class DeleteResultsExtendedTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='del-ext-user', password='password123')
        cls.suite = Suite.objects.create(name='DelExtSuite', active=True)
        cls.category = TestCategory.objects.create(category='DelExtCat')
        cls.subcategory = TestSubcategory.objects.create(subcategory='DelExtSC')
        cls.tc = TestCase.objects.create(
            name='Del Ext TC',
            test_case_id='DE-1',
            steps='Steps',
            suite=cls.suite,
            category=cls.category,
            subcategory=cls.subcategory,
            status='active',
            test_type='manual',
        )

    def _delete_url(self, suite_name=None, month=3, day=20, year=2026):
        return reverse(
            'testportal_api:delete_test_results_for_date_and_suite',
            kwargs={'suite': suite_name or self.suite.name, 'month': month, 'day': day, 'year': year},
        )

    def test_delete_success_returns_201(self):
        """Lines 34-40: successful delete returns 201."""
        TestResult.objects.create(
            result='pass', user=self.user, test_case=self.tc,
            result_date=date(2026, 3, 20), duration=1.0,
        )
        url = self._delete_url()
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TestResult.objects.filter(test_case=self.tc, result_date=date(2026, 3, 20)).count(), 0)

    def test_delete_database_error_returns_400(self):
        """Lines 36-37: DatabaseError during delete returns 400."""
        url = self._delete_url()
        with patch('testportal_api.views.test_result_views.TestResult.objects.all') as mock_all:
            mock_all.return_value.filter.return_value.delete.side_effect = DatabaseError('db error')
            response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UploadResultsExtendedTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='upload-ext-user', password='password123')
        cls.suite = Suite.objects.create(name='UploadExtSuite', active=True)
        cls.category = TestCategory.objects.create(category='UploadExtCat')
        cls.subcategory = TestSubcategory.objects.create(subcategory='UploadExtSC')
        cls.tc = TestCase.objects.create(
            name='Upload Ext TC',
            test_case_id='UE-1',
            steps='Steps',
            suite=cls.suite,
            category=cls.category,
            subcategory=cls.subcategory,
            status='active',
            test_type='manual',
        )

    def _upload_url(self, pk=None):
        return reverse('testportal_api:upload_test_results', kwargs={'pk': pk or self.suite.id})

    def _good_file(self, name='Upload Ext TC'):
        xml = _xml(_tests_node(_case_node(name=name)))
        return SimpleUploadedFile('results.xml', xml, content_type='text/xml')

    def test_no_file_returns_400(self):
        """Line 56: no file uploaded → 400."""
        self.client.login(username='upload-ext-user', password='password123')
        response = self.client.post(self._upload_url(), {'upload-results-date': '2026-03-20'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_multiple_files_returns_400(self):
        """Line 58: more than one file → 400."""
        self.client.login(username='upload-ext-user', password='password123')
        file1 = SimpleUploadedFile('a.xml', b'<x/>', content_type='text/xml')
        file2 = SimpleUploadedFile('b.xml', b'<y/>', content_type='text/xml')
        response = self.client.post(self._upload_url(), {
            'upload-results-date': '2026-03-20',
            'file1': file1,
            'file2': file2,
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_date_returns_400(self):
        """Line 61: no upload-results-date → 400."""
        self.client.login(username='upload-ext-user', password='password123')
        response = self.client.post(self._upload_url(), {
            'results_file': SimpleUploadedFile('r.xml', b'<x/>', content_type='text/xml'),
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_date_format_returns_400(self):
        """Lines 65-66: badly formatted date string → 400."""
        self.client.login(username='upload-ext-user', password='password123')
        response = self.client.post(self._upload_url(), {
            'upload-results-date': '20/03/2026',
            'results_file': SimpleUploadedFile('r.xml', b'<x/>', content_type='text/xml'),
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_suite_not_found_returns_404(self):
        """Lines 86-87: all-zeros pk, suite doesn't exist → 404."""
        self.client.login(username='upload-ext-user', password='password123')
        response = self.client.post(self._upload_url(pk=999999), {
            'upload-results-date': '2026-03-20',
            'results_file': self._good_file(),
        })

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_blank_test_case_name_in_xml_is_skipped(self):
        """Line 99: test case with no name is skipped; response is still 201."""
        self.client.login(username='upload-ext-user', password='password123')
        # XML has one case with no name Prp → name will be None → skipped
        xml = _xml(_tests_node('<Node><Prp name="status" value="0" /></Node>'))
        response = self.client.post(self._upload_url(), {
            'upload-results-date': '2026-03-20',
            'results_file': SimpleUploadedFile('r.xml', xml, content_type='text/xml'),
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unknown_test_case_goes_to_missing_cases(self):
        """Lines 103-104: test case name not in suite → added to missing_cases."""
        self.client.login(username='upload-ext-user', password='password123')
        xml = _xml(_tests_node(_case_node(name='Unknown Case That Does Not Exist')))
        response = self.client.post(self._upload_url(), {
            'upload-results-date': '2026-03-20',
            'results_file': SimpleUploadedFile('r.xml', xml, content_type='text/xml'),
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertIn('Unknown Case That Does Not Exist', data['missing_cases'])

    def test_bulk_create_database_error_returns_400(self):
        """Lines 122-123: DatabaseError during bulk_create → 400."""
        self.client.login(username='upload-ext-user', password='password123')
        with patch('testportal_api.views.test_result_views.TestResult.objects.bulk_create',
                   side_effect=DatabaseError('db error')):
            response = self.client.post(self._upload_url(), {
                'upload-results-date': '2026-03-20',
                'results_file': self._good_file(),
            })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ParseTestCaseInfoBranchTests(APITestCase):
    """Tests that exercise _parse_test_case_info branches via the upload endpoint."""

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='parse-tc-user', password='password123')
        cls.suite = Suite.objects.create(name='ParseTCSuite', active=True)
        cls.category = TestCategory.objects.create(category='ParseTCCat')
        cls.subcategory = TestSubcategory.objects.create(subcategory='ParseTCSC')
        cls.tc = TestCase.objects.create(
            name='ParseTC',
            test_case_id='PTC-1',
            steps='Steps',
            suite=cls.suite,
            category=cls.category,
            subcategory=cls.subcategory,
            status='active',
            test_type='manual',
        )

    def _upload_url(self):
        return reverse('testportal_api:upload_test_results', kwargs={'pk': self.suite.id})

    def test_non_prp_child_in_test_case_node_is_skipped(self):
        """Line 138: non-Prp child tag inside a test case node is skipped."""
        self.client.login(username='parse-tc-user', password='password123')
        # Include an <OtherTag> sibling alongside Prp elements
        extra = '<OtherTag name="ignored" value="x" />'
        xml = _xml(_tests_node(_case_node(name='ParseTC', extra=extra)))
        response = self.client.post(self._upload_url(), {
            'upload-results-date': '2026-03-20',
            'results_file': SimpleUploadedFile('r.xml', xml, content_type='text/xml'),
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_duration_value_is_set_to_none(self):
        """Lines 146-147: non-numeric duration Prp → prp_value becomes None → result saved."""
        self.client.login(username='parse-tc-user', password='password123')
        xml = _xml(_tests_node(_case_node(name='ParseTC', duration='not-a-float')))
        response = self.client.post(self._upload_url(), {
            'upload-results-date': '2026-03-20',
            'results_file': SimpleUploadedFile('r.xml', xml, content_type='text/xml'),
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = TestResult.objects.filter(test_case=self.tc).first()
        self.assertIsNotNone(created)
        self.assertIsNone(created.duration)


class ParseResultFileBranchTests(APITestCase):
    """Tests that exercise _parse_result_file project-level Prp branches."""

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='parse-rf-user', password='password123')
        cls.suite = Suite.objects.create(name='ParseRFSuite', active=True)
        cls.category = TestCategory.objects.create(category='ParseRFCat')
        cls.subcategory = TestSubcategory.objects.create(subcategory='ParseRFSC')
        cls.tc = TestCase.objects.create(
            name='ParseRFTC',
            test_case_id='PRF-1',
            steps='Steps',
            suite=cls.suite,
            category=cls.category,
            subcategory=cls.subcategory,
            status='active',
            test_type='manual',
        )

    def _upload_url(self):
        return reverse('testportal_api:upload_test_results', kwargs={'pk': self.suite.id})

    def _post_xml(self, xml_bytes):
        self.client.login(username='parse-rf-user', password='password123')
        return self.client.post(self._upload_url(), {
            'upload-results-date': '2026-03-20',
            'results_file': SimpleUploadedFile('r.xml', xml_bytes, content_type='text/xml'),
        })

    def test_project_prp_with_valid_incompletedtests_and_duration(self):
        """Lines 168, 175-177, 180-183, 187: valid project-level Prp elements are parsed."""
        xml = _xml(
            _tests_node(_case_node(name='ParseRFTC')) +
            '<Prp name="incompletedtests" value="2" />' +
            '<Prp name="duration" value="3600000" />'
        )
        response = self._post_xml(xml)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_project_prp_with_none_name_or_value_is_skipped(self):
        """Lines 172-173: Prp with no name attribute continues without error."""
        xml = _xml(
            _tests_node(_case_node(name='ParseRFTC')) +
            '<Prp />' +                              # no name, no value
            '<Prp name="somekey" />'                 # name present, no value
        )
        response = self._post_xml(xml)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_project_prp_incompletedtests_bad_int_continues(self):
        """Lines 178-179: non-integer value for incompletedtests continues without error."""
        xml = _xml(
            _tests_node(_case_node(name='ParseRFTC')) +
            '<Prp name="incompletedtests" value="not-an-integer" />'
        )
        response = self._post_xml(xml)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_project_prp_duration_bad_float_continues(self):
        """Lines 184-185: non-float value for project-level duration continues without error."""
        xml = _xml(
            _tests_node(_case_node(name='ParseRFTC')) +
            '<Prp name="duration" value="not-a-float" />'
        )
        response = self._post_xml(xml)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_no_tests_node_in_xml_returns_empty_test_cases(self):
        """Line 190: XML with no 'tests' Node → test_cases defaults to []."""
        xml = _xml('<Prp name="incompletedtests" value="0" />')
        response = self._post_xml(xml)
        # No test cases parsed, nothing to bulk_create → 201 with empty results
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data['missing_cases'], [])


class CopyResultExtendedTests(APITestCase):
    """Extended tests for copy_result_to_latest covering missing branches."""

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='copy-ext-user', password='password123')
        cls.suite = Suite.objects.create(name='CopyExtSuite', active=True)
        cls.category = TestCategory.objects.create(category='CopyExtCat')
        cls.subcategory = TestSubcategory.objects.create(subcategory='CopyExtSC')
        cls.tc = TestCase.objects.create(
            name='Copy Ext TC',
            test_case_id='CE-1',
            steps='Steps',
            suite=cls.suite,
            category=cls.category,
            subcategory=cls.subcategory,
            status='active',
            test_type='manual',
        )

    def test_copy_result_nonexistent_id_returns_404(self):
        """Lines 201-202: result_id not in DB → 404."""
        self.client.login(username='copy-ext-user', password='password123')
        url = reverse('testportal_api:copy_result_to_latest', kwargs={'result_id': 999999})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_copy_result_latest_is_none_returns_404(self):
        """Line 209: When results queryset is empty (mocked), latest_result is None → 404."""
        self.client.login(username='copy-ext-user', password='password123')
        source = TestResult.objects.create(
            result='pass', user=self.user, test_case=self.tc,
            result_date=date(2026, 1, 1), duration=1.0,
        )
        url = reverse('testportal_api:copy_result_to_latest', kwargs={'result_id': source.id})

        with patch('testportal_api.views.test_result_views.TestResult.objects.all') as mock_all:
            mock_qs = MagicMock()
            mock_qs.filter.return_value.order_by.return_value.first.return_value = None
            mock_all.return_value = mock_qs
            response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_copy_result_database_error_on_save_returns_400(self):
        """Lines 225-226: DatabaseError during save → 400."""
        self.client.login(username='copy-ext-user', password='password123')
        source = TestResult.objects.create(
            result='fail', user=self.user, test_case=self.tc,
            result_date=date(2026, 1, 1), duration=2.0,
        )
        latest = TestResult.objects.create(
            result='pass', user=self.user, test_case=self.tc,
            result_date=date(2026, 1, 2), duration=1.0,
        )
        url = reverse('testportal_api:copy_result_to_latest', kwargs={'result_id': source.id})

        with patch('testportal_api.views.test_result_views.TestResult.save',
                   side_effect=DatabaseError('save error')):
            response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
