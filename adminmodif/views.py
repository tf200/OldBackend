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
from .models import GroupMembership
from django.utils import timezone
from employees.models import EmployeeProfile
from django.http import JsonResponse , Http404
from django.db.models import Q

@api_view(['POST'])
@permission_classes([IsAdminUser])
def assign_group(request):
    serializer = AssignGroupSerializer(data=request.data)
    if serializer.is_valid():
        employee_id = serializer.validated_data['employee_id']
        
        # Find the EmployeeProfile and then the associated CustomUser
        try:
            employee_profile = EmployeeProfile.objects.get(pk=employee_id)
            user = employee_profile.user
        except EmployeeProfile.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

        group = Group.objects.get(pk=serializer.validated_data['group_id'])
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']

        # Create a new GroupMembership instance
        GroupMembership.objects.create(user=user, group=group, start_date=start_date, end_date=end_date)

        # Fetch all active group memberships for the user
        today = timezone.now().date()
        active_memberships = GroupMembership.objects.filter(
            user=user,
        ).filter(
            # Filter by memberships that are either ongoing, or end in the future, and consider null start_dates
            Q(end_date__isnull=True) | 
            Q(end_date__gte=today),
            Q(start_date__isnull=True) |
            Q(start_date__lte=today)
        ).prefetch_related('group')

        # Prepare a list of dictionaries for each group with its start and end date
        active_groups_info = [{
            'group_name': membership.group.name,
            'start_date': membership.start_date,
            'end_date': membership.end_date
        } for membership in active_memberships]

        # Return the response including the list of active groups with start and end dates
        return JsonResponse({
            'status': 'Group assigned successfully.',
            'active_groups': active_groups_info
        })
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListGroups(APIView):
    permission_classes = [IsAuthenticated]  # Or any other permission class you find suitable

    def get(self, request, format=None):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_employee_groups(request, employee_id):
    # Find the EmployeeProfile and then the associated CustomUser
    try:
        employee_profile = EmployeeProfile.objects.get(pk=employee_id)
        user = employee_profile.user
    except EmployeeProfile.DoesNotExist:
        raise Http404("Employee not found")

    # Fetch all relevant group memberships for the user
    today = timezone.now().date()
    relevant_memberships = GroupMembership.objects.filter(
        user=user,
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=today),
        Q(start_date__isnull=True) | Q(start_date__lte=today)
    ).prefetch_related('group')

    # Prepare a list of dictionaries for each group with its start and end date
    groups_info = [{
        'group_name': membership.group.name,
        'start_date': membership.start_date,
        'end_date': membership.end_date
    } for membership in relevant_memberships]

    # Return the response including the list of groups
    return JsonResponse({
        'employee_id': employee_id,
        'groups': groups_info
    })