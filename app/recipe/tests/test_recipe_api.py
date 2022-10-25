"""Test recipe APIS"""

from decimal import Decimal
import tempfile
import os
from PIL import Image


from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import  APIClient

from core.models import (
    Recipe,
    Tag,
    Ingredient
)

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    IngredientSerializer
)

RECIPE_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """Create and return a recipe details URL. """
    return reverse('recipe:recipe-detail',args=[recipe_id])

def image_upload_url(image_id):
    """Create and return an image upload URL"""
    return reverse('recipe:recipe-upload-image', args=[image_id])

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

        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipe =Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

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

    def test_full_update(self):
        """Test full update of recipe."""
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link='https://exmaple.com/recipe.pdf',
            description='Sample recipe description.',
        )

        payload = {
            'title': 'New recipe title',
            'link': 'https://example.com/new-recipe.pdf',
            'description': 'New recipe description',
            'time_minutes': 10,
            'price': Decimal('2.50'),
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe successful."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete another users recipe gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tag(self):
        """Test to create a recipe with tag value"""
        payload = {
            'title':'Thai Pawn fried rice',
            'time_minutes' :30,
            'price':Decimal('3.6'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],
        }

        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(),1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(),2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tag(self):
        """Test create recipe using existing tag"""
        tag_indian = Tag.objects.create(user=self.user,name='Indian')

        payload = {
            'title' : 'Idli',
            'time_minutes':10,
            'price':Decimal('4.5'),
            'tags':[{'name':'Indian'},{'name':'breakfast'}]
        }

        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(),1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(),2)
        self.assertIn(tag_indian,recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user= self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_on_update(self):
        """Test create tag when update recipe"""

        recipe = create_recipe(user=self.user)

        payload = { 'tags': [{'name':'Lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url,payload, format='json')

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Lunch')
        self.assertIn(new_tag,recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe"""
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user,name='Lunch')
        payload = {'tags' : [{'name':'Lunch'}]}
        url = detail_url(recipe.id)

        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertIn(tag_lunch,recipe.tags.all())
        self.assertNotIn(tag_breakfast,recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing the recipe tags"""
        tag = Tag.objects.create(user=self.user, name='Dessert')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {'tags':[]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(),0)

    def test_create_recipe_with_new_ingredients(self):
        """Test creating a recipe with new ingredients. """
        payload = {
            'title': 'Cauliflower Tacos',
            'time_minutes':60,
            'price': Decimal('4.6'),
            'ingredients' : [{'name':'Cauliflower'},{'name':'Salt'}],
        }

        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(),1)
        recipe = recipes[0]

        self.assertEqual(recipe.ingredients.count(),2)
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredient(self):
        """Test creating a new recipe with existing ingredients"""
        ingredient = Ingredient.objects.create(user=self.user, name='Lemon')
        payload = {
            'title':'Vietnamese Soup',
            'time_minutes': 25,
            'price':Decimal('4.8'),
            'ingredients':[{'name':'Lemon'},{'name':'Fish'}]
        }

        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(),1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(),2)
        self.assertIn(ingredient, recipe.ingredients.all())
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_ingredients_on_update(self):
        """Test creating an ingredients when update recipe"""

        recipe = create_recipe(user=self.user)

        payload = {'ingredients':[{'name':'Lime'}]}
        url = detail_url(recipe.id)
        res =self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(user=self.user)
        self.assertEqual(new_ingredient,recipe.ingredients.all()[0])

    def test_update_recipe_assign_ingredient(self):
        """Test assigning an existing ingredient when updating a recipe."""
        ingredient1 = Ingredient.objects.create(user=self.user, name='Pepper')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)

        ingredient2 = Ingredient.objects.create(user=self.user, name='Chili')
        payload = {'ingredients': [{'name': 'Chili'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """Test clearing a recipes ingredients."""
        ingredient = Ingredient.objects.create(user=self.user, name='Garlic')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload = {'ingredients': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

class ImageUploadTests(TestCase):
    """Tests for the image upload API. """

    def setUp(self):
        self.client=APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'password123',
        )
        self.client.force_authenticate(self.user)
        self.recipe=create_recipe(user=self.user)

    def tearDown(self) -> None:
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test upload the image in recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10,10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image':image_file}
            res = self.client.post(url, payload, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertIn('image',res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Uploading bad image request"""
        url = image_upload_url(self.recipe.id)
        payload = {'image': 'notanimage'}
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
