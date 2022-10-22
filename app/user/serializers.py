"""
Serializers for the user API view
"""
from django.contrib.auth import get_user_model

from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ['email','password','name']
        extra_kwargs = {'password': {'write_only': True, 'min_lenght': 5}}

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)