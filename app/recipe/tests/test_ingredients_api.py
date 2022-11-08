"""
Test for the ingredients API.
"""

from decimal import Decimal

from unicodedata import name
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient,Recipe

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

def detail_url(ingredient_id):
    """Create and return an ingredient details URL. """
    return reverse('recipe:ingredient-detail',args=[ingredient_id])

def create_user(email='user@example.com',password='testpass123'):
    """Create test user and return"""
    return get_user_model().objects.create_user(email,password)

class PublicIngredientApiTests(TestCase):
    """Test authenticated API request"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retriving ingredients. """
        res = self.client.get(INGREDIENTS_URL)
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
        Ingredient.objects.create(user=self.user,name='Vanilla')

        res = self.client.get(INGREDIENTS_URL)

        ingredient = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredient, many=True)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test list of ingredients is limited to authenticated user"""

        user2 =create_user(email='user2@example.com')
        Ingredient.objects.create(user=user2, name='Salt')
        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'],ingredient.name)
        self.assertEqual(res.data[0]['id'],ingredient.id)

    def test_update_ingredient(self):
        """testing and updating an ingredients"""
        ingredient = Ingredient.objects.create(user=self.user, name='Cilantro')

        payload = {'name':'Coriander'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url,payload)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """test deleting Ingredient """
        ingredient = Ingredient.objects.create(user=self.user, name='pepper')

        url = detail_url(ingredient.id)
        res =self.client.delete(url)

        self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)
        ingredient = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredient.exists())

    def test_filter_ingredients_to_recipe(self):
        """Test ingredients assign to recipe"""
        in1 = Ingredient.objects.create(user=self.user, name='Apple')
        in2 = Ingredient.objects.create(user=self.user, name='Turkey')

        recipe = Recipe.objects.create(
            title='Apple Crumble',
            time_minutes=60,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe.ingredients.add(in1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only':1})

        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)

        self.assertIn(s1.data,res.data)
        self.assertNotIn(s2.data,res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients return a unique list"""

        ing = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Lentils')
        recipe1 = Recipe.objects.create(
            title='Eggs Benedict',
            time_minutes=60,
            price=Decimal('7.00'),
            user=self.user,
        )

        recipe2 =Recipe.objects.create(
            title='Herbs Eggs',
            time_minutes=20,
            price=Decimal('4.00'),
            user=self.user,
        )

        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENTS_URL,{'assigned_only':1})

        self.assertEqual(len(res.data),1)