"""Serializers for recipe API"""

from dataclasses import field
from pyexpat import model
from rest_framework import serializers

from core.models import Recipe, Tag

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe"""

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe details view"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']

class TagSerialize(serializers.ModelSerializer):
    """Serializer for Tag """

    class Meta:
        model=Tag
        field=['id','name']
        read_only_fields = ['id']
