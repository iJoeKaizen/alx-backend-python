# chats/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import User, Conversation, Message
from .serializers import (
    UserSerializer,
    ConversationSerializer,
    MessageSerializer,
    ConversationDetailSerializer
)
from django.db.models import Q

class ConversationListCreate(generics.ListCreateAPIView):
    """Create new conversations and list user's conversations"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConversationSerializer
    
    def get_queryset(self):
        """Return conversations for the current user"""
        return Conversation.objects.filter(participants=self.request.user).order_by('-updated_at')
    
    def create(self, request, *args, **kwargs):
        """Create a new conversation with participants"""
        # Add current user to participants if not included
        participants = request.data.get('participants', [])
        if str(request.user.user_id) not in participants:
            participants.append(str(request.user.user_id))
        
        # Create serializer with updated participants
        serializer = self.get_serializer(data={
            **request.data,
            'participants': participants
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        # Return detailed conversation representation
        detail_serializer = ConversationDetailSerializer(
            instance=serializer.instance,
            context=self.get_serializer_context()
        )
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class ConversationDetail(generics.RetrieveUpdateDestroyAPIView):
    """Manage individual conversations"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConversationDetailSerializer
    lookup_field = 'conversation_id'
    lookup_url_kwarg = 'conversation_id'
    
    def get_queryset(self):
        """Only allow access to conversations where user is participant"""
        return Conversation.objects.filter(participants=self.request.user)

class ConversationMessages(generics.ListAPIView):
    """List messages in a conversation"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        """Get messages for the conversation, ensuring user is participant"""
        conversation_id = self.kwargs['conversation_id']
        
        # Verify user is in conversation
        if not Conversation.objects.filter(
            conversation_id=conversation_id,
            participants=self.request.user
        ).exists():
            return Message.objects.none()
        
        return Message.objects.filter(
            conversation_id=conversation_id
        ).order_by('sent_at')

class MessageListCreate(generics.ListCreateAPIView):
    """Send messages and list user's messages"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        """Return messages for the current user's conversations"""
        return Message.objects.filter(
            Q(conversation__participants=self.request.user) | 
            Q(sender=self.request.user)
        ).distinct().order_by('-sent_at')
    
    def create(self, request, *args, **kwargs):
        """Create a new message in a conversation"""
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
        
        # Set sender to current user
        request.data['sender'] = str(request.user.user_id)
        
        # Set is_read to False if not provided
        if 'is_read' not in request.data:
            request.data['is_read'] = False
        
        return super().create(request, *args, **kwargs)

class MessageDetail(generics.RetrieveUpdateDestroyAPIView):
    """Manage individual messages"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer
    lookup_field = 'message_id'
    lookup_url_kwarg = 'message_id'
    
    def get_queryset(self):
        """Only allow access to messages in user's conversations"""
        return Message.objects.filter(
            Q(conversation__participants=self.request.user) | 
            Q(sender=self.request.user)
        ).distinct()

class MessageMarkRead(generics.UpdateAPIView):
    """Mark a message as read"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer
    lookup_field = 'message_id'
    lookup_url_kwarg = 'message_id'
    
    def get_queryset(self):
        """Only allow access to messages in user's conversations"""
        return Message.objects.filter(
            conversation__participants=self.request.user
        ).exclude(sender=self.request.user)
    
    def update(self, request, *args, **kwargs):
        message = self.get_object()
        message.is_read = True
        message.save()
        return Response({'status': 'message marked as read'})

# User views
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class UserDetail(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'user_id'

class CurrentUserDetail(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
