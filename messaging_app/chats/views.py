from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, Conversation, Message
from .serializers import (
    UserSerializer,
    ConversationSerializer,
    MessageSerializer,
    ConversationDetailSerializer
)
from django.db.models import Q

class UserViewSet(viewsets.ModelViewSet):
    """Viewset for user management"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'user_id'

    def get_permissions(self):
        """Custom permissions for user actions"""
        if self.action in ['create']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_object(self):
        """Get user by user_id"""
        if self.kwargs.get('user_id') == 'me':
            return self.request.user
        return super().get_object()

class ConversationViewSet(viewsets.ModelViewSet):
    """Viewset for conversation management"""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'conversation_id'

    def get_queryset(self):
        """Return conversations for the current user"""
        user = self.request.user
        return Conversation.objects.filter(participants=user).order_by('-updated_at')

    def get_serializer_class(self):
        """Use detailed serializer for retrieve/list actions"""
        if self.action in ['retrieve', 'list']:
            return ConversationDetailSerializer
        return ConversationSerializer

    def create(self, request, *args, **kwargs):
        """Create a new conversation with participants"""
        # Add current user to participants if not already included
        if 'participants' not in request.data:
            request.data['participants'] = []
        
        if request.user.user_id not in [str(uid) for uid in request.data['participants']]:
            request.data['participants'].append(str(request.user.user_id))
        
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['get'], url_path='messages')
    def list_messages(self, request, conversation_id=None):
        """List messages in a conversation"""
        conversation = self.get_object()
        messages = conversation.messages.all().order_by('sent_at')
        page = self.paginate_queryset(messages)
        
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    """Viewset for message management"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'message_id'

    def get_queryset(self):
        """Return messages for the current user's conversations"""
        user = self.request.user
        return Message.objects.filter(
            Q(conversation_id__participants=user) | 
            Q(sender=user)
        ).distinct().order_by('-sent_at')

    def create(self, request, *args, **kwargs):
        """Create a new message in a conversation"""
        # Automatically set sender to current user
        request.data['sender'] = str(request.user.user_id)
        
        # Set is_read to False for new messages
        if 'is_read' not in request.data:
            request.data['is_read'] = False
        
        # Validate conversation exists and user is participant
        conversation_id = request.data.get('conversation_id')
        if not conversation_id:
            return Response(
                {'conversation_id': 'This field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
            if request.user not in conversation.participants.all():
                return Response(
                    {'detail': 'You are not a participant in this conversation'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Conversation.DoesNotExist:
            return Response(
                {'conversation_id': 'Invalid conversation ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_as_read(self, request, message_id=None):
        """Mark a message as read"""
        message = self.get_object()
        
        # Only the recipient can mark as read
        if request.user != message.sender:
            message.is_read = True
            message.save()
            return Response({'status': 'message marked as read'})
        
        return Response(
            {'detail': 'You cannot mark your own messages as read'},
            status=status.HTTP_403_FORBIDDEN
        )
