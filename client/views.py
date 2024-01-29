from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import ClientDetailsSerializer
from .models import ClientDetails
# Create your views here.
class ClientDetailsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientDetailsSerializer
    queryset = ClientDetails.objects.all()



# class ClientListView (generics.ListAPIView) : 

    


