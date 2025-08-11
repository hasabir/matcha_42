from django.urls import path, include


from .views import create_user

urlpatterns = [
    path('create/', create_user),
]