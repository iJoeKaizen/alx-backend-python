from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Message, MessageHistory
from django.contrib.auth import get_user_model

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
                # Get current user (requires middleware context)
                editor = None
                try:
                    from django.utils.functional import SimpleLazyObject
                    from django.contrib.auth.middleware import get_user

                    # Try to get user from request thread local
                    request = getattr(Message, 'request', None)
                    if request and isinstance(request.user, (User, SimpleLazyObject)):
                        editor = request.user
                except ImportError:
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
