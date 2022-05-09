from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Review
        fields = ['id', 'content', 'owner', 'movieId', 'star', 'createdAt', 'updatedAt']

