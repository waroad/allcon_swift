from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    # path('reviews/<int:pk>/', views.CommentList.as_view()),
    path('<int:pk>/', views.ReviewDetail.as_view()),
    path('all/', views.ReviewAll.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
