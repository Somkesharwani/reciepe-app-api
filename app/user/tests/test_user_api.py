"""test for the user API"""

import email
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL=reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    """Create and return user. """
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """ Test the pubic feature of the user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test create a user is successful. """
        payload={
            'email': 'test@test.com',
            'password': 'testpass123',
            'name':'Test Name',
        }

        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        user=get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password',res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user already exists"""

        payload = {
            'email': 'test@email.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }

        create_user(**payload)
        res=self.client.post(CREATE_USER_URL,payload)

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error  is returned if password is short than  5 chars """
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL,payload)

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        user_exists= get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """test generate token for valid credential"""
        user_details ={
            'name': 'Test Name',
            'email': 'test@test.com',
            'password': 'test-user-password',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }

        res =self.client.post(TOKEN_URL,payload)

        self.assertIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_200_OK)

    def test_create_token_bad_credential(self):
        """test return error if credential invalid"""
        create_user(email='test@test.com', password='test-user-password')

        payload = {'email':'test@test.com','password':'badpass'}

        res = self.client.post(TOKEN_URL,payload)

        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password return a error. """
        payload ={'email':'test@test.com', 'password': ''}
        res=self.client.post(TOKEN_URL,payload)

        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users"""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)

class PrivateUserAPI(TestCase):
    """Test API request that required authentications. """

    def setUp(self):
        self.user = create_user(
            email='test@test.com',
            password='testpass123',
            name='TestName',
        )
        self.client=APIClient()
        self.client.force_authenticate(user=self.user)

    def test_post_me_not_allowed(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,{
            'name':self.user.name,
            'email':self.user.email,
        })

    def test_post_me_not_allowed(self):
        """test Post is not allowed for the me endpoint"""

        res =self.client.post(ME_URL,{})

        self.assertEqual(res.status_code,status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user ."""
        payload = { 'name': 'Update name','password':'newpassword123'}

        res = self.client.patch(ME_URL,payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code,status.HTTP_200_OK)
