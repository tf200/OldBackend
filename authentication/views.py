from django.shortcuts import render
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyCustomTokenObtainPairSerializer , LocationSerializer
from .models import Location
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyCustomTokenObtainPairSerializer
# Create your views here.



class LocationCreateAPIView(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer