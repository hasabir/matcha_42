from django.shortcuts import render

import json
from django.shortcuts import render
from django.http import JsonResponse
from .models import User
from django.forms.models import model_to_dict
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import UserSerializer

@api_view(['POST'])
def create_user(request, *args, **kwargs):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        instance = serializer.save()
        return Response(UserSerializer(instance).data, status=201)
    return Response(serializer.errors, status=400)
