"""Unit tests for MSG-001: Message model.

Verify model fields, Meta options, and string representation.
"""
from django.test import TestCase
from django.contrib.auth.models import User

from apps.msg.models import Message


class MessageModelTests(TestCase):
    """Tests for MSG-001: Message model."""

    def setUp(self):
        self.receiver = User.objects.create_user(
            username='receiver', password='pass1234',
        )
        self.sender = User.objects.create_user(
            username='sender', password='pass1234',
        )

    def test_create_message_with_required_fields(self):
        """Message can be created with all required fields."""
        msg = Message.objects.create(
            receiver=self.receiver,
            type=Message.MessageType.SYSTEM,
            title='System Notice',
            content='Welcome to the platform.',
        )
        self.assertEqual(msg.receiver, self.receiver)
        self.assertIsNone(msg.sender)
        self.assertEqual(msg.type, Message.MessageType.SYSTEM)
        self.assertEqual(msg.title, 'System Notice')
        self.assertEqual(msg.content, 'Welcome to the platform.')
        self.assertFalse(msg.is_read)
        self.assertEqual(msg.related_type, '')
        self.assertIsNone(msg.related_id)
        self.assertIsNotNone(msg.created_at)

    def test_create_message_with_all_fields(self):
        """Message can be created with all fields including optional ones."""
        msg = Message.objects.create(
            receiver=self.receiver,
            sender=self.sender,
            type=Message.MessageType.AUDIT_APPROVED,
            title='Audit Passed',
            content='Your enterprise has been approved.',
            is_read=True,
            related_type='enterprise',
            related_id=42,
        )
        self.assertEqual(msg.sender, self.sender)
        self.assertTrue(msg.is_read)
        self.assertEqual(msg.related_type, 'enterprise')
        self.assertEqual(msg.related_id, 42)

    def test_message_type_choices(self):
        """MessageType should have the 4 expected choices."""
        choices = dict(Message.MessageType.choices)
        self.assertIn('AUDIT_APPROVED', choices)
        self.assertIn('AUDIT_REJECTED', choices)
        self.assertIn('CONTACT_RECEIVED', choices)
        self.assertIn('SYSTEM', choices)

    def test_message_db_table(self):
        """Model should use 'msg_message' as db_table."""
        self.assertEqual(Message._meta.db_table, 'msg_message')

    def test_message_ordering(self):
        """Model should order by -created_at."""
        self.assertEqual(Message._meta.ordering, ['-created_at'])

    def test_message_str(self):
        """String representation should show id and title."""
        msg = Message.objects.create(
            receiver=self.receiver,
            type=Message.MessageType.SYSTEM,
            title='Test Title',
            content='Test content',
        )
        self.assertIn('Test Title', str(msg))

    def test_message_ordering_in_queryset(self):
        """Newer messages should come first in default queryset."""
        msg1 = Message.objects.create(
            receiver=self.receiver,
            type=Message.MessageType.SYSTEM,
            title='First',
            content='First message',
        )
        msg2 = Message.objects.create(
            receiver=self.receiver,
            type=Message.MessageType.SYSTEM,
            title='Second',
            content='Second message',
        )
        messages = list(Message.objects.filter(id__in=[msg1.id, msg2.id]))
        self.assertEqual(messages[0].id, msg2.id)
        self.assertEqual(messages[1].id, msg1.id)

    def test_receiver_related_name(self):
        """User should have 'messages' related_name for received messages."""
        msg = Message.objects.create(
            receiver=self.receiver,
            type=Message.MessageType.SYSTEM,
            title='Related',
            content='Test related name',
        )
        self.assertIn(msg, self.receiver.messages.all())

    def test_sender_related_name(self):
        """User should have 'sent_messages' related_name for sent messages."""
        msg = Message.objects.create(
            receiver=self.receiver,
            sender=self.sender,
            type=Message.MessageType.SYSTEM,
            title='Related',
            content='Test sender related name',
        )
        self.assertIn(msg, self.sender.sent_messages.all())

    def test_sender_can_be_null(self):
        """Messages without a sender should be valid (system messages)."""
        msg = Message.objects.create(
            receiver=self.receiver,
            type=Message.MessageType.SYSTEM,
            title='No sender',
            content='System message without sender',
        )
        self.assertIsNone(msg.sender)
