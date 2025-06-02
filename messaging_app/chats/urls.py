# chats/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'conversations', views.ConversationViewSet, basename='conversation')
router.register(r'messages', views.MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
    
    # Additional custom endpoints
    path('conversations/<uuid:conversation_id>/messages/', 
         views.ConversationViewSet.as_view({'get': 'list_messages'}), 
         name='conversation-messages'),
]
