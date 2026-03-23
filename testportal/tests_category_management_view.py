from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from testportal.models import Suite, TestCategory, TestSubcategory


class CategoryManagementViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username='cat-user', password='password123')
        cls.admin_user = user_model.objects.create_superuser(username='cat-admin', password='password123', email='cat-admin@test.local')
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
