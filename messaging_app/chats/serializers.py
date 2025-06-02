from rest_framework import serializers
from .models import User, Conversation, Message
import uuid

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""
    user_id = serializers.UUIDField(default=uuid.uuid4, read_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = [
            'user_id', 'email', 'password', 
            'first_name', 'last_name', 'phone_number',
            'online_status', 'last_activity'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def create(self, validated_data):
        """Create and return a user with encrypted password"""
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data.get('phone_number', ''),
        )
        return user
    
    def update(self, instance, validated_data):
        """Update and return user"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        return user

class MessageSerializer(serializers.ModelSerializer):
    """Serializer for the Message model"""
    sender = UserSerializer(read_only=True)
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='sender',
        write_only=True
    )
    
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'sender_id',
            'content', 'timestamp', 'is_read'
        ]
        read_only_fields = ['id', 'timestamp', 'is_read']
        extra_kwargs = {
            'conversation': {'write_only': True}
        }

class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for the Conversation model with nested messages"""
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        source='participants',
        write_only=True
    )
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'participant_ids',
            'created_at', 'updated_at', 'messages'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create a conversation with participants"""
        participants = validated_data.pop('participants')
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.set(participants)
        return conversation

class ConversationDetailSerializer(ConversationSerializer):
    """Serializer for conversation details with nested messages"""
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields