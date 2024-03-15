from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from urllib.parse import urlencode
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.permissions import IsAuthenticated

# Create your views here.
from rest_framework.generics import ListAPIView
from .models import Conversation , Message
from .serializers import ConversationSerializer , MessageSerializer , ConversationLookupSerializer

class UserConversationsAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer

    def get_queryset(self):
        # Get the user from the request
        user = self.request.user.id
        # Return conversations involving the authenticated user
        return Conversation.objects.filter(involved=user)


class ConversationMessagesAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        conversation_id = self.kwargs['conv_id']
        return Message.objects.filter(conversation__id=conversation_id).order_by('timestamp')
    


def serialize_user(user):
    # Serialize user details here. Adjust fields as needed.
    return {
        'id': user.id,
        'name': f'{user.profile.first_name} {user.profile.last_name}',
          # Include other fields you want to return
    }

@require_http_methods(["GET"])
def get_conversation_messages(request, conv_id):
    try:
        conversation = Conversation.objects.get(id=conv_id)
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversation not found'}, status=404)
    
    involved_users = [serialize_user(user) for user in conversation.involved.all()]

    messages_qs = Message.objects.filter(conversation=conversation).order_by('-timestamp')
    
    # Pagination setup
    page_number = request.GET.get('page', 1)
    limit = request.GET.get('limit', 20)  # Default to 10 items per page
    paginator = Paginator(messages_qs, limit)
    
    try:
        messages_page = paginator.page(page_number)
    except PageNotAnInteger:
        messages_page = paginator.page(1)
    except EmptyPage:
        messages_page = paginator.page(paginator.num_pages)
    
    # Constructing next and previous URLs
    base_url = request.build_absolute_uri(reverse('conversation_messages', kwargs={'conv_id': conv_id}))
    query_params = request.GET.copy()
    if messages_page.has_next():
        query_params['page'] = messages_page.next_page_number()
        next_url = f"{base_url}?{urlencode(query_params)}"
    else:
        next_url = None

    if messages_page.has_previous():
        query_params['page'] = messages_page.previous_page_number()
        previous_url = f"{base_url}?{urlencode(query_params)}"
    else:
        previous_url = None

    serialized_messages = [{
        'id': message.id,
        'sender': message.sender.id,
        'conversation': message.conversation.id,
        'content': message.content,
        'timestamp': message.timestamp.isoformat(),
        'read_status': message.read_status,
    } for message in messages_page]

    response_data = {
        'next': next_url,
        'previous': previous_url,
        'count': paginator.count,
        'page_size': limit,
        'involved': involved_users,
        'results': serialized_messages,
    }

    return JsonResponse(response_data)



class ConversationLookupView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = ConversationLookupSerializer(data=request.data)
        if serializer.is_valid():
            conversation = serializer.save()
            if conversation:
                return Response({'conversation_id': conversation.id})
            return Response({'error': 'Invalid user IDs or users do not exist'}, status=400)
        return Response(serializer.errors, status=400)