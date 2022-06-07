from rest_framework import serializers
from .models import Movie
from django.contrib.auth.models import User


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'createdAt', 'updatedAt', 'content', 'liked', 'imageURL', 'movieURL',
                  'likeCount', 'currentUser']
