"""Test for Django admin modification """

import email
from unicodedata import name
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

class AdminSiteTests(TestCase):
    """Test for Django admin"""

    def setUp(self):
        self.client=Client()
        self.admin_user=get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='Testuser123'
        )

        self.client.force_login(self.admin_user)

        self.user=get_user_model().objects.create_user(
            email='user@example.com',
            password='Testpass123',
            name='Test user'
        )

    def test_users_list(self):
        """Test user listed on the page"""

        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        print(res)
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test the edit user page works."""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)


    def test_create_user_page(self):
        """Test the create user page works."""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)