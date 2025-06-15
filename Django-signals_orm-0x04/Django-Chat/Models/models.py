from django.db import models
from django.conf import settings
from django.utils import timezone

class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    # Add edited tracking fields
    edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)  # Changed to edited_at

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"

class MessageHistory(models.Model):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='history'
    )
    old_content = models.TextField()
    edited_at = models.DateTimeField(default=timezone.now)  # Consistent naming
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-edited_at']
        verbose_name_plural = "Message Histories"

    def __str__(self):
        return f"History for message #{self.message.id} at {self.edited_at}"
