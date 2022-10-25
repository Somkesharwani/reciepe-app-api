"""Create View for Recipe API"""

from rest_framework import (
    viewsets,
    mixins
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render

from core.models import Recipe,Tag
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View to manage recipe APIs. """
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrievve recipe for authenticate user. """
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create new recipe"""
        serializer.save(user=self.request.user)

class TagViewSet(mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet):
    """Manage tag in the database """
    serializer_class = serializers.TagSerialize
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')








