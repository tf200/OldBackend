from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .serializer import AssignGroupSerializer , GroupSerializer
from django.contrib.auth.models import  Group
from authentication.models import CustomUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAdminUser])  # Ensure only admins can access this endpoint
def assign_group(request):
    serializer = AssignGroupSerializer(data=request.data)
    if serializer.is_valid():
        user = CustomUser.objects.get(pk=serializer.validated_data['user_id'])
        group = Group.objects.get(pk=serializer.validated_data['group_id'])
        user.groups.add(group)
        return Response({'status': 'group assigned'})
    else:
        return Response(serializer.errors, status=400)


class ListGroups(APIView):
    permission_classes = [IsAuthenticated]  # Or any other permission class you find suitable

    def get(self, request, format=None):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)



class UserGroupsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        groups = user.groups.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)