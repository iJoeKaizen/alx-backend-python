import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import EmailValidator

class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser with UUID primary key
    and additional fields for messaging functionality.
    """
    # Primary key using UUID
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    
    # Required fields
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        verbose_name='email address'
    )
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    
    # Optional fields
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Activity tracking
    last_activity = models.DateTimeField(default=timezone.now)
    online_status = models.BooleanField(default=False)
    
    # Authentication configuration
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class Conversation(models.Model):
    """
    Model representing a conversation between multiple users.
    Uses UUID primary key and tracks creation/update timestamps.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    participants = models.ManyToManyField(
        User,
        related_name='conversations',
        help_text='Users participating in this conversation'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
    
    def __str__(self):
        participants = self.participants.all()
        names = [f"{user.first_name} {user.last_name}" for user in participants]
        return f"Conversation: {', '.join(names)}"

class Message(models.Model):
    """
    Model representing a message within a conversation.
    Contains sender reference, conversation reference, content, and status.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    conversation = models.ForeignKey(
        Conversation,
        related_name='messages',
        on_delete=models.CASCADE,
        help_text='Conversation this message belongs to'
    )
    sender = models.ForeignKey(
        User,
        related_name='sent_messages',
        on_delete=models.CASCADE,
        help_text='User who sent this message'
    )
    content = models.TextField(help_text='Actual message content')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(
        default=False,
        help_text='Has the message been read by the recipient?'
    )
    
    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
    
    def __str__(self):
        return f"{self.sender.email}: {self.content[:50]}"
