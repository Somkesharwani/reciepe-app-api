"""Serializers for recipe API"""

from rest_framework import serializers

from core.models import (
    Recipe,
     Tag,
)

class TagSerialize(serializers.ModelSerializer):
    """Serializer for Tag """

    class Meta:
        model=Tag
        fields=['id','name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe"""
    tags =TagSerialize(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link','tags']
        read_only_fields = ['id']

    def create(self,validated_data):
        """Create a recipe Tag."""
        tags = validated_data.pop('tag',[])
        recipe = Recipe.objects.create(**validated_data)
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj,created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

        return recipe


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe details view"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']


