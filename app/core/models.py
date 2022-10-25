"""
Database models
"""
from distutils.command.upload import upload
import uuid
import os
from turtle import title
from unittest.util import _MAX_LENGTH
from django.conf import settings
from email.policy import default
from enum import unique
from django.db import models
from django.contrib.auth.models import(
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('upload','recipe',filename)


class UserManager(BaseUserManager):
    """Manager  user field"""

    def create_user(self,email,password=None,**extra_field):
        """Create , save and return a new user"""
        if not email:
            raise ValueError('User must have an email address')
        user=self.model(email=self.normalize_email(email),**extra_field)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self,email,password):
        """Create and return a new super user"""
        user=self.create_user(email,password)
        user.is_staff=True
        user.is_superuser=True
        user.save(using=self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email=models.EmailField(max_length=255,unique=True)
    name=models.CharField(max_length=255)
    is_active=models.BooleanField(default = True)
    is_staff=models.BooleanField(default=False)

    objects=UserManager()

    USERNAME_FIELD = 'email'

class Recipe(models.Model):
    """Recipe Object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5,decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title

class Tag(models.Model):
    """Tag for filtering recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    def __str__(self):
        return self.name

class Ingredient(models.Model):
    """Adding Ingredient for recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return self.name