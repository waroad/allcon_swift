import ast
import datetime

from django.utils import timezone
from reviews.models import Review
from reviews.serializers import ReviewSerializer
from .models import Movie
from .serializers import MovieSerializer
from rest_framework import generics, permissions, status
from .permission import IsOwnerOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Case, When
from django.conf import settings
from django.db import models
from django.db.models import FloatField
from django.db.models.functions import Cast


class MovieList(generics.ListCreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset=Movie.objects.all()
        # query = queryset.get(pk=self.kwargs.get('pk'))
        return queryset

    def create(self, request, *args, **kwargs):
        for query in self.get_queryset():
            print(query.content)
            if query.content==request.data['content']:
                return Response("Already Exist:"+str(query.id), status=status.HTTP_200_OK)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MovieDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


class LikeMovie(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, pk):
        # print(request.get_full_path())
        current_board=Movie.objects.get(id=pk)
        like_count_before=current_board.liker.all().count()
        current_board.liker.add(self.request.user)
        current_board.likeCount = current_board.liker.all().count()
        if current_board.likeCount!=like_count_before:
            current_board.save()
            return Response("successfully liked the board")
        else:
            return Response("already liked the board")


class ReviewList(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        self_review=Review.objects.filter(owner=self.request.user, movieId=self.kwargs['pk'])
        if self_review:
            queryset = Review.objects.filter(movieId=self.kwargs['pk']).exclude(owner=self.request.user).reverse()
            queryset= list(self_review) + list(queryset)
        else:
            queryset = Review.objects.filter(movieId=self.kwargs['pk']).reverse()
        return queryset
