from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from testportal.access import CATEGORY_MANAGER_GROUP_NAME
from testportal.models import Suite, TestCategory, TestSubcategory, TestCase as PortalTestCase


class CategoryManagementViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='cat-user', password='password123')
        cls.category_manager_user = user_model.objects.create_user(username='cat-manager', password='password123')
        cls.admin_user = user_model.objects.create_superuser(username='cat-admin', password='password123', email='cat-admin@test.local')
        category_manager_group, _ = Group.objects.get_or_create(name=CATEGORY_MANAGER_GROUP_NAME)
        cls.category_manager_user.groups.add(category_manager_group)
        cls.suite = Suite.objects.create(name='CatSuite', active=True)
        cls.category = TestCategory.objects.create(category='Existing Category')
        cls.subcategory = TestSubcategory.objects.create(subcategory='Existing Subcategory')

    def test_anonymous_user_cannot_access_category_management_view(self):
        response = self.client.get(reverse('testportal:category_management_view'))

        self.assertEqual(response.status_code, 403)

    def test_non_admin_user_cannot_access_category_management_view(self):
        self.client.login(username='cat-user', password='password123')
        response = self.client.get(reverse('testportal:category_management_view'))

        self.assertEqual(response.status_code, 403)

    def test_admin_user_category_management_view_renders(self):
        self.client.login(username='cat-admin', password='password123')
        response = self.client.get(reverse('testportal:category_management_view'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Categories')
        self.assertContains(response, 'Subcategories')
        self.assertContains(response, 'Existing Category')
        self.assertContains(response, 'Existing Subcategory')

    def test_category_manager_user_category_management_view_renders(self):
        self.client.login(username='cat-manager', password='password123')
        response = self.client.get(reverse('testportal:category_management_view'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Categories')
        self.assertContains(response, 'Subcategories')

    def test_admin_user_can_add_category_and_subcategory(self):
        self.client.login(username='cat-admin', password='password123')

        response = self.client.post(reverse('testportal:category_management_view'), {
            'action': 'add-category',
            'category': 'New Category',
        })
        self.assertContains(response, 'Category added.')

        response = self.client.post(reverse('testportal:category_management_view'), {
            'action': 'add-subcategory',
            'subcategory': 'New Subcategory',
        })
        self.assertContains(response, 'Subcategory added.')

        self.assertTrue(TestCategory.objects.filter(category='New Category').exists())
        self.assertTrue(TestSubcategory.objects.filter(subcategory='New Subcategory').exists())

    def test_admin_user_can_remove_category_and_subcategory(self):
        self.client.login(username='cat-admin', password='password123')

        response = self.client.post(reverse('testportal:category_management_view'), {
            'action': 'delete-category',
            'category_id': self.category.id,
        })
        self.assertContains(response, 'Category removed.')

        response = self.client.post(reverse('testportal:category_management_view'), {
            'action': 'delete-subcategory',
            'subcategory_id': self.subcategory.id,
        })
        self.assertContains(response, 'Subcategory removed.')

        self.assertFalse(TestCategory.objects.filter(id=self.category.id).exists())
        self.assertFalse(TestSubcategory.objects.filter(id=self.subcategory.id).exists())

    def test_category_manager_user_can_add_category_and_subcategory(self):
        self.client.login(username='cat-manager', password='password123')

        response = self.client.post(reverse('testportal:category_management_view'), {
            'action': 'add-category',
            'category': 'Manager Category',
        })
        self.assertContains(response, 'Category added.')

        response = self.client.post(reverse('testportal:category_management_view'), {
            'action': 'add-subcategory',
            'subcategory': 'Manager Subcategory',
        })
        self.assertContains(response, 'Subcategory added.')

        self.assertTrue(TestCategory.objects.filter(category='Manager Category').exists())
        self.assertTrue(TestSubcategory.objects.filter(subcategory='Manager Subcategory').exists())

    def test_delete_missing_category_is_noop(self):
        self.client.login(username='cat-admin', password='password123')

        response = self.client.post(reverse('testportal:category_management_view'), {
            'action': 'delete-category',
            'category_id': 999999,
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(TestCategory.objects.filter(id=self.category.id).exists())

    def test_delete_missing_subcategory_is_noop(self):
        self.client.login(username='cat-admin', password='password123')

        response = self.client.post(reverse('testportal:category_management_view'), {
            'action': 'delete-subcategory',
            'subcategory_id': 999999,
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(TestSubcategory.objects.filter(id=self.subcategory.id).exists())

    def test_delete_in_use_category_shows_error(self):
        self.client.login(username='cat-admin', password='password123')
        PortalTestCase.objects.create(
            name='Cat Protected TC',
            test_case_id='CAT-PROT-1',
            steps='Steps',
            suite=self.suite,
            category=self.category,
            subcategory=self.subcategory,
        )

        response = self.client.post(reverse('testportal:category_management_view'), {
            'action': 'delete-category',
            'category_id': self.category.id,
        })

        self.assertContains(response, 'Cannot remove category because test cases still reference it.')
        self.assertTrue(TestCategory.objects.filter(id=self.category.id).exists())

    def test_delete_in_use_subcategory_shows_error(self):
        self.client.login(username='cat-admin', password='password123')
        PortalTestCase.objects.create(
            name='Subcat Protected TC',
            test_case_id='CAT-PROT-2',
            steps='Steps',
            suite=self.suite,
            category=self.category,
            subcategory=self.subcategory,
        )

        response = self.client.post(reverse('testportal:category_management_view'), {
            'action': 'delete-subcategory',
            'subcategory_id': self.subcategory.id,
        })

        self.assertContains(response, 'Cannot remove subcategory because test cases still reference it.')
        self.assertTrue(TestSubcategory.objects.filter(id=self.subcategory.id).exists())
