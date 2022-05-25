from .models import SearchResult
from rest_framework import serializers

class SearchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchResult
        fields = ['title', 'url', 'href', 'site']