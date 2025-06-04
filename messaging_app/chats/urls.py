# chats/urls.py

from django.urls import path, include
from rest_framework import routers
from rest_framework_nested.routers import NestedDefaultRouter
from .views import UserViewSet, ConversationViewSet, MessageViewSet

# Base router (explicit DefaultRouter)
base_router = routers.DefaultRouter()
base_router.register(r'users', UserViewSet, basename='user')
base_router.register(r'conversations', ConversationViewSet, basename='conversation')

# Nested router for messages under conversations
conversation_router = NestedDefaultRouter(base_router, r'conversations', lookup='conversation')
conversation_router.register(r'messages', MessageViewSet, basename='conversation-messages')

# Final urlpatterns
urlpatterns = [
    path('', include(base_router.urls)),
    path('', include(conversation_router.urls)),
]
