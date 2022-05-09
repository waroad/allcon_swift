from .models import Review
from .serializers import ReviewSerializer
from rest_framework import generics
from rest_framework import permissions
from ..users.models import Profile
from .permissions import IsOwnerOrReadOnly
from django.db.models import Case, When

from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.db import models


# class CommentList(generics.ListCreateAPIView):
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly,
#                           IsOwnerOrReadOnly]
#
#     def get_serializer_class(self):
#         if self.request.method=="GET":
#             return BoardSerializer
#         else:
#             return CommentSerializer
#
#     def get_queryset(self):
#         user = self.request.user
#         comments=Comment.objects.filter(owner=user)
#         arr=[]
#         for comment in comments:
#             if comment.boardId.id not in arr:
#                 arr.append(comment.boardId.id)
#         preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(arr)])
#         return Board.objects.filter(pk__in=arr).order_by(preserved)
#
#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)
#         profile = Profile.objects.get(user=self.request.user)
#         profile.count+=1
#         profile.save()


class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def perform_destroy(self, serializer):
        print("------------------------wow",self.request.user)
        serializer.delete()


class ReviewAll(generics.ListAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]