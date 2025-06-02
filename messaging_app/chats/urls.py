# chats/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'conversations', views.ConversationViewSet, basename='conversation')
router.register(r'messages', views.MessageViewSet, basename='message')

# The API URLs are now determined automatically by the router
urlpatterns = [
    # Include all router-generated URLs
    path('', include(router.urls)),
    
    # Add custom endpoints that aren't covered by the router
    path(
        'conversations/<uuid:conversation_id>/messages/',
        views.ConversationViewSet.as_view({'get': 'list_messages'}),
        name='conversation-messages'
    ),
]
