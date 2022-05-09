import ast
import datetime

from django.utils import timezone
from ..reviews.models import Review
from ..reviews.serializers import ReviewSerializer
from .models import Board
from .serializers import BoardSerializer
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
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset=Board.objects.all()
        # query = queryset.get(pk=self.kwargs.get('pk'))
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        vote_texts=ast.literal_eval(serializer.data['voteText'])


class MovieDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


class LikeMovie(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, pk):
        # print(request.get_full_path())
        current_board=Board.objects.get(id=pk)
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
        queryset = Review.objects.filter(boardId=self.kwargs['pk']).reverse()
        return queryset
