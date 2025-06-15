from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, MessageHistory
import datetime

User = get_user_model()

class MessageEditSignalTests(TestCase):
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
        self.editor = User.objects.create_user(
            username='editor',
            email='editor@example.com',
            password='testpass123'
        )
        
        # Create initial message
        self.message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original content"
        )
    
    def test_edit_history_created_on_content_change(self):
        """Test history is created when message content changes"""
        # Simulate editor in view
        self.message._editor = self.editor
        self.message.content = "Updated content"
        self.message.save()
        
        self.assertEqual(MessageHistory.objects.count(), 1)
        history = MessageHistory.objects.first()
        self.assertEqual(history.old_content, "Original content")
        self.assertEqual(history.message, self.message)
        self.assertEqual(history.edited_by, self.editor)
        self.assertTrue(self.message.edited)
        self.assertIsNotNone(self.message.last_edited)
    
    def test_no_history_on_non_content_change(self):
        """Test history not created when non-content fields change"""
        original_content = self.message.content
        self.message.is_read = True
        self.message.save()
        
        self.assertEqual(MessageHistory.objects.count(), 0)
        self.assertFalse(self.message.edited)
        self.assertEqual(self.message.content, original_content)
    
    def test_multiple_edits_create_multiple_history(self):
        """Test multiple edits create multiple history records"""
        # First edit
        self.message.content = "First edit"
        self.message.save()
        
        # Second edit
        self.message.content = "Second edit"
        self.message.save()
        
        self.assertEqual(MessageHistory.objects.count(), 2)
        histories = MessageHistory.objects.order_by('edit_timestamp')
        self.assertEqual(histories[0].old_content, "Original content")
        self.assertEqual(histories[1].old_content, "First edit")
    
    def test_editor_tracking(self):
        """Test editor is captured when set in view"""
        self.message._editor = self.editor
        self.message.content = "Edited content"
        self.message.save()
        
        history = MessageHistory.objects.first()
        self.assertEqual(history.edited_by, self.editor)
    
    def test_editor_null_when_not_set(self):
        """Test editor is null when not set"""
        self.message.content = "Edited without editor"
        self.message.save()
        
        history = MessageHistory.objects.first()
        self.assertIsNone(history.edited_by)
    
    def test_edited_flag_only_set_on_content_change(self):
        """Test edited flag is only set when content changes"""
        # First change (content)
        self.message.content = "New content"
        self.message.save()
        self.assertTrue(self.message.edited)
        
        # Second change (non-content)
        original_edited_state = self.message.edited
        self.message.is_read = True
        self.message.save()
        self.assertEqual(self.message.edited, original_edited_state)
