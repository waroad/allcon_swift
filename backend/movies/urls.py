from django.urls import path
from .views import *

urlpatterns = [
    path('', MovieList.as_view()),
    path('<int:pk>/', MovieDetail.as_view()),
    path('<int:pk>/like/', LikeMovie.as_view()),
    path('<int:pk>/reviews/', ReviewList.as_view()),
]
