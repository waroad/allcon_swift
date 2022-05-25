from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path('search_result/', csrf_exempt(views.Search.as_view())),
]
