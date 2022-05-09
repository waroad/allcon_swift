from rest_framework import serializers
from .models import Board
from django.contrib.auth.models import User


class BoardSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Board
        fields = ['id', 'createdAt', 'updatedAt', 'content', 'liker',
                  'likeCount', 'currentUser']
