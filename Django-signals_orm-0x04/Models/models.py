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
    edited = models.BooleanField(default=False)  # Track if message has been edited
    last_edited = models.DateTimeField(null=True, blank=True)  # Track last edit time

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"

class MessageHistory(models.Model):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='history'
    )
    old_content = models.TextField()
    edit_timestamp = models.DateTimeField(default=timezone.now)
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return f"History for message #{self.message.id} at {self.edit_timestamp}"

    class Meta:
        ordering = ['-edit_timestamp']
        verbose_name_plural = "Message Histories"
