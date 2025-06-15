from django.db.models.signals import pre_delete, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..Models.models import Message, Notification, MessageHistory  # Adjust import if path differs

User = get_user_model()

# ---------- USER DELETION SIGNALS ----------

@receiver(pre_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    """
    Handles cleanup of related data before user deletion
    """
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()
    Notification.objects.filter(user=instance).delete()
    MessageHistory.objects.filter(edited_by=instance).update(edited_by=None)

@receiver(post_delete, sender=User)
def log_user_deletion(sender, instance, **kwargs):
    """
    Logs user deletion
    """
    print(f"User {instance.username} (ID: {instance.id}) has been deleted.")

# ---------- MESSAGE EDIT TRACKING ----------

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Logs message history before editing, sets edit flags
    """
    if not instance.pk:
        return  # New message, skip

    try:
        original = Message.objects.get(pk=instance.pk)
        if original.content != instance.content:
            editor = getattr(instance, '_editor', None)

            MessageHistory.objects.create(
                message=instance,
                old_content=original.content,
                edited_by=editor
            )

            instance.edited = True
            instance.edited_at = timezone.now()
    except Message.DoesNotExist:
        pass
