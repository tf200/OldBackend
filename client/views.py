from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import ClientDetails
from django_filters.rest_framework import DjangoFilterBackend
from client.filters import ClientDiagnosisFilter
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
    filter_backends = [DjangoFilterBackend]


class ClientUpdateView(generics.UpdateAPIView) :
    permission_classes = [IsAuthenticated]
    serializer_class = ClientDetailsSerializer
    queryset = ClientDetails.objects.all()


class ClientDeleteView(generics.DestroyAPIView) : 
    permission_classes = [IsAuthenticated]
    serializer_class = ClientDetailsSerializer
    queryset = ClientDetails.objects.all()

#====================================================
    


class DiagnosisCreateView(generics.CreateAPIView) :
    permission_classes = [IsAuthenticated]
    serializer_class = ClientDiagnosisSerializer



class DiagnosisRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientDiagnosisSerializer
    queryset = ClientDiagnosis.objects.all()



class DiagnosisListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientDiagnosisSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ClientDiagnosisFilter

    def get_queryset(self):
        client_id = self.kwargs['client'] 
        return ClientDiagnosis.objects.filter(client=client_id)


class DiagnosisUpdateView(generics.UpdateAPIView) :
    permission_classes = [IsAuthenticated]
    serializer_class = ClientDiagnosisSerializer
    queryset = ClientDiagnosis.objects.all()


class DiagnosisDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientDiagnosisSerializer
    queryset = ClientDiagnosis.objects.all()
  
#=======================================================================
    


class ClientEmergencyContactCreateView(generics.CreateAPIView) :
    permission_classes = [IsAuthenticated]
    serializer_class = ClientEmergencyContactSerializer



class ClientEmergencyContactRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientEmergencyContactSerializer
    queryset = ClientEmergencyContact.objects.all()



class ClientEmergencyContactListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientEmergencyContactSerializer

    def get_queryset(self):
        client_id = self.kwargs['client'] 
        return ClientEmergencyContact.objects.filter(client=client_id)


class ClientEmergencyContactUpdateView(generics.UpdateAPIView) :
    permission_classes = [IsAuthenticated]
    serializer_class = ClientEmergencyContactSerializer
    queryset = ClientEmergencyContact.objects.all()


class ClientEmergencyContactDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientEmergencyContactSerializer
    queryset = ClientEmergencyContact.objects.all()