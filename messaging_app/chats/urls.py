# chats/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Conversation endpoints
    path('conversations/', views.ConversationListCreate.as_view(), name='conversation-list'),
    path('conversations/<uuid:conversation_id>/', views.ConversationDetail.as_view(), name='conversation-detail'),
    path('conversations/<uuid:conversation_id>/messages/', views.ConversationMessages.as_view(), name='conversation-messages'),
    
    # Message endpoints
    path('messages/', views.MessageListCreate.as_view(), name='message-list'),
    path('messages/<uuid:message_id>/', views.MessageDetail.as_view(), name='message-detail'),
    path('messages/<uuid:message_id>/mark-read/', views.MessageMarkRead.as_view(), name='message-mark-read'),
    
    # User endpoints
    path('users/', views.UserList.as_view(), name='user-list'),
    path('users/<uuid:user_id>/', views.UserDetail.as_view(), name='user-detail'),
    path('users/me/', views.CurrentUserDetail.as_view(), name='current-user'),
]
