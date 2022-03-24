from django.test import TestCase
from django.contrib.auth.models import User

from core.models import Suite


class Test_Create_Suite(TestCase):

    @classmethod
    def setUpTestData(cls):
        test_suite = Suite.objects.create(name='Test1', active=True)

    def test_suite_content(self):
        suite = Suite.suiteobjects.get(id=1)
        name = f'{suite.name}'
        active = suite.active

        self.assertEqual(name, 'Test1')
        self.assertTrue(active)

        self.assertEqual(str(suite), '<Test1, active=True>')