"""Test for Django admin modification """

import email
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

class AdminSiteTests(TestCase):
    """Test for Django admin"""

    def setUp(self):
        self.client=Client()
        self.admin_user=get_user_model().objects.create_user(
            email='admin@gmail.com',
            password='Testuser123',
            name='Super user'
        )

        self.client.force_login(self.admin_user)

        self.user=get_user_model().objects.create_user(
            email='user@gmail.com',
            password='Testpass123',
            name='Test user'
        )

    def test_users_list(self):
        """Test user listed on the page"""

        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res,self.user.name)
        self.assertContains(res,self.user.email)