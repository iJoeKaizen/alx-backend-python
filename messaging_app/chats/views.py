from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Conversation, Message
from .serializers import (
    UserSerializer,
    ConversationSerializer,
    MessageSerializer,
    ConversationDetailSerializer
)
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

class UserViewSet(viewsets.ModelViewSet):
    """Viewset for user management with filtering"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'user_id'
    
    # Add filtering capabilities
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'last_login']
    ordering = ['-date_joined']

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_object(self):
        if self.kwargs.get('user_id') == 'me':
            return self.request.user
        return super().get_object()

class ConversationViewSet(viewsets.ModelViewSet):
    """Viewset for conversation management with advanced filtering"""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'conversation_id'
    
    # Add comprehensive filtering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'created_at': ['gte', 'lte', 'exact'],
        'updated_at': ['gte', 'lte', 'exact'],
    }
    search_fields = ['participants__username', 'participants__email']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']

    def get_queryset(self):
        user = self.request.user
        queryset = Conversation.objects.filter(participants=user).order_by('-updated_at')
        
        # Additional filtering for participants
        participant_ids = self.request.query_params.getlist('participants')
        if participant_ids:
            queryset = queryset.filter(
                participants__user_id__in=participant_ids
            ).distinct()
            
        return queryset

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return ConversationDetailSerializer
        return ConversationSerializer

    def create(self, request, *args, **kwargs):
        if 'participants' not in request.data:
            request.data['participants'] = []
        
        if request.user.user_id not in [str(uid) for uid in request.data['participants']]:
            request.data['participants'].append(str(request.user.user_id))
        
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['get'], url_path='messages')
    def list_messages(self, request, conversation_id=None):
        conversation = self.get_object()
        messages = conversation.messages.all().order_by('sent_at')
        
        # Add filtering to messages endpoint
        is_read = request.query_params.get('is_read')
        if is_read in ['true', 'false']:
            messages = messages.filter(is_read=is_read.lower() == 'true')
            
        sender_id = request.query_params.get('sender')
        if sender_id:
            messages = messages.filter(sender__user_id=sender_id)
            
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    """Viewset for message management with advanced filtering"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'message_id'
    
    # Add comprehensive filtering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'sent_at': ['gte', 'lte', 'exact'],
        'is_read': ['exact'],
    }
    search_fields = ['content', 'sender__username']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']

    def get_queryset(self):
        user = self.request.user
        queryset = Message.objects.filter(
            Q(conversation_id__participants=user) | 
            Q(sender=user)
        ).distinct().order_by('-sent_at')
        
        # Additional filtering parameters
        conversation_id = self.request.query_params.get('conversation')
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)
            
        sender_id = self.request.query_params.get('sender')
        if sender_id:
            queryset = queryset.filter(sender__user_id=sender_id)
            
        # Time-based filtering (last 24 hours, last week, etc.)
        time_range = self.request.query_params.get('time_range')
        if time_range == 'last_24h':
            cutoff = timezone.now() - timedelta(hours=24)
            queryset = queryset.filter(sent_at__gte=cutoff)
        elif time_range == 'last_week':
            cutoff = timezone.now() - timedelta(days=7)
            queryset = queryset.filter(sent_at__gte=cutoff)
            
        return queryset

    def create(self, request, *args, **kwargs):
        request.data['sender'] = str(request.user.user_id)
        
        if 'is_read' not in request.data:
            request.data['is_read'] = False
        
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
        message = self.get_object()
        
        if request.user != message.sender:
            message.is_read = True
            message.save()
            return Response({'status': 'message marked as read'})
        
        return Response(
            {'detail': 'You cannot mark your own messages as read'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    @action(detail=False, methods=['post'], url_path='mark-conversation-read')
    def mark_conversation_read(self, request):
        """Mark all unread messages in a conversation as read"""
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
            
            # Update all unread messages in the conversation
            updated = Message.objects.filter(
                conversation_id=conversation,
                is_read=False
            ).exclude(sender=request.user).update(is_read=True)
            
            return Response({
                'status': f'{updated} messages marked as read',
                'conversation_id': str(conversation_id)
            })
            
        except Conversation.DoesNotExist:
            return Response(
                {'conversation_id': 'Invalid conversation ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
