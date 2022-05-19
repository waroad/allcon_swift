import ast
import datetime

from django.utils import timezone
from django.contrib.auth.models import User
from reviews.models import Review
from reviews.serializers import ReviewSerializer
from .models import Movie
from .serializers import MovieSerializer
from rest_framework import generics, permissions, status
from .permission import IsOwnerOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import Profile
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
        user_liked_movies_list = ast.literal_eval(request.user.profile.searchedMovies)
        if request.data['content'] in user_liked_movies_list:
            user_liked_movies_list.remove(request.data['content'])
        user_liked_movies_list.insert(0,request.data['content'])
        if len(user_liked_movies_list)>20:
            user_liked_movies_list.pop()
        request.user.profile.searchedMovies = str(user_liked_movies_list)
        request.user.profile.save()
        for query in self.get_queryset():
            if query.content==request.data['content']:
                self.kwargs["pk"]=query.id
                return generics.RetrieveAPIView.retrieve(self=self,request=request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MovieDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_object(self):
        queryset=self.get_queryset()
        obj = queryset.get(pk=self.kwargs.get('pk'))
        obj.liked=0
        if obj.liker.filter(username=self.request.user).exists():
            obj.liked=1
        obj.save()
        return obj


class LikeMovie(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, pk):
        # print(request.get_full_path())
        user_liked_movies_list = ast.literal_eval(request.user.profile.likedMovies)
        current_board=Movie.objects.get(id=pk)
        movie_name = current_board.content
        print(movie_name)
        like_count_before=current_board.liker.all().count()
        current_board.liker.add(self.request.user)
        current_board.likeCount = current_board.liker.all().count()
        if current_board.likeCount!=like_count_before:
            user_liked_movies_list.insert(0,movie_name)
            request.user.profile.likedMovies = str(user_liked_movies_list)
            request.user.profile.save()
            current_board.save()
            return Response("successfully liked the movie")
        else:
            user_liked_movies_list.remove(movie_name)
            request.user.profile.likedMovies = str(user_liked_movies_list)
            request.user.profile.save()
            current_board.liker.remove(self.request.user)
            current_board.likeCount -= 1
            current_board.save()
            return Response("successfully disliked the movie")


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
