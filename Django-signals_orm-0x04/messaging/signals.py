from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Message, MessageHistory
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Logs message content before it's edited
    """
    if instance.pk:  # Only for existing messages (edits)
        try:
            original = Message.objects.get(pk=instance.pk)
            if original.content != instance.content:  # Content changed
                # Get current user (if available)
                editor = None
                try:
                    # Check if editor was set in the view
                    if hasattr(instance, '_editor'):
                        editor = instance._editor
                    # Fallback to request-based approach
                    elif hasattr(Message, 'request'):
                        request = Message.request
                        if request and hasattr(request, 'user'):
                            editor = request.user
                except Exception:
                    pass
                
                # Create history record
                MessageHistory.objects.create(
                    message=instance,
                    old_content=original.content,
                    edited_by=editor
                )
                
                # Update message flags
                instance.edited = True
                instance.last_edited = timezone.now()
        except Message.DoesNotExist:
            pass  # New message, nothing to log
