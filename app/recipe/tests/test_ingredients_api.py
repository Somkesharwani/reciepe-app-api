"""
Test for the ingredients API.
"""

import imp
from unicodedata import name
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INFREDIENTS_URL = reverse('recipe:ingredients-list')

def create_user(email='user@example.com',password='testpass123'):
    """Create test user and return"""
    return get_user_model().objects.create_user(email,password)

class PublicIngredientApiTests(TestCase):
    """Test authenticated API request"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retriving ingredients. """
        res = self.client.get(INFREDIENTS_URL)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientsApiTests(TestCase):
    """Test unauthenticated API requests. """

    def setUp(self):
        self.user=create_user()
        self.client=APIClient()
        self.client.force_authenticate(self.user)

    def test_reterieve_ingredients(self):
        """Test retriving a list of Ingredients. """
        Ingredient.objects.create(user=self.user,name='Kale')
        Ingredient.objects.create(userr=self.user,name='Vanilla')

        res = self.client.get(INFREDIENTS_URL)

        ingredient = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredient, many=True)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test list of ingredients is limited to authenticated user"""

        user2 =create_user(email='user2@example.com')
        Ingredient.objects.create(user=user2, name='Salt')
        ingredients = Ingredient.objects.create(user=self.user, name='Pepper')

        res = self.client.get(INFREDIENTS_URL)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'],ingredients.name)
        self.assertEqual(res.data[0]['id'],ingredients.id)