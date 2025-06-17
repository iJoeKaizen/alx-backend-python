import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Custom user model with UUID primary key and additional fields"""
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name='User ID'
    )
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        verbose_name='email address'
    )
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    last_activity = models.DateTimeField(default=timezone.now)
    online_status = models.BooleanField(default=False)
    
    # Password field is inherited from AbstractUser
    password = models.CharField(_("password"), max_length=128)
    
    # Authentication configuration
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class Conversation(models.Model):
    """Model representing a conversation between users"""
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='Conversation ID'
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
    """Model representing a message within a conversation"""
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='Message ID'
    )
    conversation_id = models.ForeignKey(
        Conversation,
        related_name='messages',
        on_delete=models.CASCADE,
        help_text='Conversation this message belongs to',
        db_column='conversation_id'
    )
    sender = models.ForeignKey(
        User,
        related_name='sent_messages',
        on_delete=models.CASCADE,
        help_text='User who sent this message',
        db_column='sender_id'
    )
    message_body = models.TextField(
        help_text='Content of the message',
        verbose_name='Message Body'
    )
    sent_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Sent At'
    )
    is_read = models.BooleanField(
        default=False,
        help_text='Has the message been read by the recipient?'
    )
    
    class Meta:
        ordering = ['sent_at']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
    
    def __str__(self):
        return f"{self.sender.email}: {self.message_body[:50]}"
