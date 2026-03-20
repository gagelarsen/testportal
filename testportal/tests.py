from django.test import TestCase

from testportal.models import Suite


class TestCreateSuite(TestCase):

    @classmethod
    def setUpTestData(cls):
        Suite.objects.create(name='Test1', active=True)

    def test_suite_content(self):
        suite = Suite.objects.get(id=1)

        self.assertEqual(suite.name, 'Test1')
        self.assertTrue(suite.active)

        self.assertEqual(str(suite), 'Test1')