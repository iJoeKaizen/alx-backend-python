from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from ..Models.models import Message, Notification, MessageHistory

User = get_user_model()

@receiver(pre_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    """
    Pre-delete signal to handle cascading deletions
    """
    # Delete all messages where user is sender or receiver
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()
    
    # Delete all notifications for the user
    Notification.objects.filter(user=instance).delete()
    
    # Update MessageHistory to set edited_by to None
    MessageHistory.objects.filter(edited_by=instance).update(edited_by=None)

@receiver(post_delete, sender=User)
def log_user_deletion(sender, instance, **kwargs):
    """
    Post-delete signal for logging or additional cleanup
    """
    # Could be used for logging, analytics, or additional cleanup
    print(f"User {instance.username} (ID: {instance.id}) has been deleted.")
