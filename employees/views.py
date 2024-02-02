from django.shortcuts import render

# Create your views here.


from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import UserEmployeeProfileSerializer
from rest_framework.response import Response







class CurrentUserProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserEmployeeProfileSerializer(request.user)
        return Response(serializer.data)