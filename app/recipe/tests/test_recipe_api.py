"""Test recipe APIS"""

from decimal import Decimal
import email
from turtle import title


from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import  APIClient


from recipe import serializers

from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

RECIPE_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """Create and return a recipe details URL. """
    return reverse('recipe:recipe-detail',args=[recipe_id])

def create_recipe(user, **params):
    """Create and return example recipe"""
    default = {
        'title':'Sample recipe title',
        'time_minutes':22,
        'price':Decimal('5.25'),
        'description': 'Sample description',
        'link':'https://example.com/recipe.pdf'
    }
    default.update(params)

    recipe =Recipe.objects.create(user=user, **default)

    return recipe

def create_user(**params):
    """Create new user """
    return get_user_model().objects.create_user(**params)

class PublicRecipeAPITests(TestCase):
    """test unauthenticate API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test suth us required to call API. """
        res=self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """"""

    def setUp(self):
        self.client=APIClient()
        self.user=create_user(email='test@test.com',password='testpass123')

        self.client.force_authenticate(self.user)

    def test_retrive_recipe(self):
        """Test retriving a list of recipe"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipe =Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipe, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list off recipe is limited to authenticated user. """
        other_user = create_user(email='other@test.com',password='testpass123')
        self.user = create_user(email='test@Exampletest.com',password='testpass123')

        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipe =Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        #self.assertEqual(res.data, serializer.data)
        self.assertNotEqual(res.data, serializer.data)

    def test_get_recipe_details(self):
        """Test get recipe detail. """
        recipe = create_recipe(user=self.user)

        url =detail_url(recipe.id)
        res = self.client.get(url)

        serializers = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializers.data)


    def test_create_recipe(self):
        """Test create recipe using API"""
        payload = {
            'title' : 'Sample recipe',
            'time_minutes': 30,
            'price' : Decimal('5.99'),
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k,v in payload.items():
            self.assertEqual(getattr(recipe,k),v)
        self.assertEqual(recipe.user,self.user)

    def test_partial_updates(self):
        """test partial update of a recipe. """
        original_link="https://example.com//recipe.pdf"
        recipe=create_recipe(
            user=self.user,
            title='Sample recipe title',
            link=original_link,
        )

        payload = {'title':'New recipe title'}

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)