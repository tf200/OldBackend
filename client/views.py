from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import ClientDetails
# Create your views here.



class ClientCreateView(generics.CreateAPIView) :
    permission_classes = [IsAuthenticated]
    serializer_class = ClientDetailsSerializer


    



class ClientDetailsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientDetailsSerializer
    queryset = ClientDetails.objects.all()



class ClientListView (generics.ListAPIView) : 
    permission_classes = [IsAuthenticated]
    serializer_class = ClientDetailsSerializer
    queryset = ClientDetails.objects.all()

    


class DiagnosisCreateView(generics.CreateAPIView) :
    permission_classes = [IsAuthenticated]
    serializer_class = ClientDiagnosisSerializer



class DiagnosisRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientDiagnosisSerializer
    queryset = ClientDiagnosis.objects.all()
    lookup_field = 'client'



class DiagnosisListView (generics.ListAPIView) : 
    permission_classes = [IsAuthenticated]
    serializer_class = ClientDiagnosisSerializer
    queryset = ClientDiagnosis.objects.all()