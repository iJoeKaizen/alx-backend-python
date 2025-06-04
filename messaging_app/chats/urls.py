# chats/urls.py

from django.urls import path, include
from rest_framework_nested.routers import NestedDefaultRouter
from .views import UserViewSet, ConversationViewSet, MessageViewSet

# Root router
router = NestedDefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Nested router for messages under conversations
conversations_router = NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

# Define URL patterns
urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),
]
