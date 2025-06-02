# chats/views.py
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
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'user_id'

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_object(self):
        if self.kwargs.get('user_id') == 'me':
            return self.request.user
        return super().get_object()

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'conversation_id'

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(participants=user).order_by('-updated_at')

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return ConversationDetailSerializer
        return ConversationSerializer

    def create(self, request, *args, **kwargs):
        # Add current user to participants if not included
        participants = request.data.get('participants', [])
        if str(request.user.user_id) not in participants:
            participants.append(str(request.user.user_id))
            request.data['participants'] = participants
            
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def messages(self, request, conversation_id=None):
        """List messages in a conversation"""
        conversation = self.get_object()
        messages = conversation.messages.all().order_by('sent_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'message_id'

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            Q(conversation__participants=user) | 
            Q(sender=user)
        ).distinct().order_by('-sent_at')

    def create(self, request, *args, **kwargs):
        # Automatically set sender to current user
        request.data['sender'] = str(request.user.user_id)
        
        # Set is_read to False for new messages
        request.data.setdefault('is_read', False)
        
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

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
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
