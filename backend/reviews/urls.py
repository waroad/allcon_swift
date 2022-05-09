from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('reviews/', views.ReviewList.as_view()),
    path('reviews/<int:pk>/', views.ReviewDetail.as_view()),
    path('reviews/all/', views.ReviewAll.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
