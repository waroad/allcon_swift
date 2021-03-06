import ast

from django.http import JsonResponse
from rest_framework import generics, status
from django.contrib.auth.models import User
from rest_framework import permissions
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response


class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def update(self, request, *args, **kwargs):
        request.user.profile.taste = str(request.data['taste'])
        request.user.profile.save()
        return generics.RetrieveAPIView.retrieve(self=self, request=request)


class UserDelete(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user=self.request.user
        user.delete()

        return JsonResponse({"result":"user delete"})


class UserCurrent(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        queryset = self.get_queryset()
        obj = queryset.get(username=self.request.user)
        return obj
