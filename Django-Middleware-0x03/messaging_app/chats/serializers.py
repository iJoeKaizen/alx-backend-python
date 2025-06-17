from rest_framework import serializers
from .models import User, Conversation, Message
import uuid
import re

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model with custom validation"""
    user_id = serializers.UUIDField(default=uuid.uuid4, read_only=True)
    password = serializers.CharField(
        write_only=True, 
        style={'input_type': 'password'},
        min_length=8,
        error_messages={
            'min_length': 'Password must be at least 8 characters long.'
        }
    )
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    
    # SerializerMethodField for full name
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'user_id', 'email', 'password', 
            'first_name', 'last_name', 'full_name',
            'phone_number', 'online_status', 'last_activity'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def get_full_name(self, obj):
        """SerializerMethodField to get user's full name"""
        return f"{obj.first_name} {obj.last_name}"
    
    def validate_email(self, value):
        """Custom validation for email format"""
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", value):
            raise serializers.ValidationError("Invalid email format")
        return value
    
    def validate_phone_number(self, value):
        """Custom validation for phone number format"""
        if value and not re.match(r"^\+?[0-9]{10,15}$", value):
            raise serializers.ValidationError(
                "Phone number must be 10-15 digits, optionally starting with '+'"
            )
        return value
    
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
    """Serializer for the Message model with custom fields"""
    sender = UserSerializer(read_only=True)
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='sender',
        write_only=True
    )
    
    # SerializerMethodField for formatted timestamp
    formatted_sent_at = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'message_id', 'conversation_id', 'sender', 'sender_id',
            'message_body', 'sent_at', 'formatted_sent_at', 'is_read'
        ]
        read_only_fields = ['message_id', 'sent_at', 'is_read']
    
    def get_formatted_sent_at(self, obj):
        """Return human-readable timestamp"""
        return obj.sent_at.strftime("%Y-%m-%d %H:%M:%S")
    
    def validate_message_body(self, value):
        """Validate message content"""
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Message cannot be empty")
        if len(value) > 1000:
            raise serializers.ValidationError("Message is too long (max 1000 characters)")
        return value

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
    
    # SerializerMethodField for unread message count
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'participant_ids',
            'created_at', 'updated_at', 'messages', 'unread_count'
        ]
        read_only_fields = ['conversation_id', 'created_at', 'updated_at']
    
    def get_unread_count(self, obj):
        """Count of unread messages for current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0
    
    def validate_participant_ids(self, value):
        """Validate conversation participants"""
        if len(value) < 2:
            raise serializers.ValidationError(
                "A conversation must have at least 2 participants"
            )
        if len(value) > 10:
            raise serializers.ValidationError(
                "A conversation can have at most 10 participants"
            )
        return value
    
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
