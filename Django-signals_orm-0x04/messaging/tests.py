from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Notification

User = get_user_model()

class SignalTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@example.com',
            password='testpass123'
        )
        self.receiver = User.objects.create_user(
            username='receiver',
            email='receiver@example.com',
            password='testpass123'
        )
    
    def test_notification_created_on_new_message(self):
        # Create a new message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello, this is a test message"
        )
        
        # Verify notification was created
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        
        # Check notification properties
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.is_read)
        
    def test_no_notification_on_message_update(self):
        # Create initial message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Initial content"
        )
        
        # Clear notifications
        Notification.objects.all().delete()
        
        # Update the message
        message.content = "Updated content"
        message.save()
        
        # Verify no new notification was created
        self.assertEqual(Notification.objects.count(), 0)
