"""Unit tests for MSG-005: create_notification helper.

Verify the helper function creates messages correctly for use by other modules.
"""
from django.test import TestCase
from django.contrib.auth.models import User

from apps.msg.models import Message
from apps.msg.views import create_notification


class CreateNotificationTests(TestCase):
    """Tests for MSG-005: create_notification helper."""

    def setUp(self):
        self.receiver = User.objects.create_user(
            username='receiver', password='pass1234',
        )
        self.sender = User.objects.create_user(
            username='sender', password='pass1234',
        )

    def test_create_notification_basic(self):
        """create_notification should create a message with required fields."""
        msg = create_notification(
            receiver=self.receiver,
            type=Message.MessageType.SYSTEM,
            title='Welcome',
            content='Welcome to the platform.',
        )
        self.assertIsNotNone(msg.id)
        self.assertEqual(msg.receiver, self.receiver)
        self.assertEqual(msg.type, Message.MessageType.SYSTEM)
        self.assertEqual(msg.title, 'Welcome')
        self.assertEqual(msg.content, 'Welcome to the platform.')
        self.assertFalse(msg.is_read)
        self.assertIsNone(msg.sender)
        self.assertEqual(msg.related_type, '')
        self.assertIsNone(msg.related_id)

    def test_create_notification_with_sender(self):
        """create_notification should set sender when provided."""
        msg = create_notification(
            receiver=self.receiver,
            type=Message.MessageType.CONTACT_RECEIVED,
            title='Contact Received',
            content='Someone shared their contact.',
            sender=self.sender,
        )
        self.assertEqual(msg.sender, self.sender)

    def test_create_notification_with_related_object(self):
        """create_notification should set related_type and related_id."""
        msg = create_notification(
            receiver=self.receiver,
            type=Message.MessageType.AUDIT_APPROVED,
            title='Audit Approved',
            content='Your enterprise audit passed.',
            related_type='enterprise',
            related_id=42,
        )
        self.assertEqual(msg.related_type, 'enterprise')
        self.assertEqual(msg.related_id, 42)

    def test_create_notification_with_all_fields(self):
        """create_notification should handle all fields correctly."""
        msg = create_notification(
            receiver=self.receiver,
            type=Message.MessageType.AUDIT_REJECTED,
            title='Audit Rejected',
            content='Your enterprise audit was rejected.',
            sender=self.sender,
            related_type='enterprise',
            related_id=99,
        )
        self.assertEqual(msg.receiver, self.receiver)
        self.assertEqual(msg.sender, self.sender)
        self.assertEqual(msg.type, Message.MessageType.AUDIT_REJECTED)
        self.assertEqual(msg.title, 'Audit Rejected')
        self.assertEqual(msg.content, 'Your enterprise audit was rejected.')
        self.assertEqual(msg.related_type, 'enterprise')
        self.assertEqual(msg.related_id, 99)

    def test_create_notification_returns_message_instance(self):
        """create_notification should return a Message instance."""
        msg = create_notification(
            receiver=self.receiver,
            type=Message.MessageType.SYSTEM,
            title='Test',
            content='Test',
        )
        self.assertIsInstance(msg, Message)

    def test_create_notification_persists_to_db(self):
        """Message should be persisted in the database."""
        msg = create_notification(
            receiver=self.receiver,
            type=Message.MessageType.SYSTEM,
            title='Persist',
            content='Persist test',
        )
        db_msg = Message.objects.get(id=msg.id)
        self.assertEqual(db_msg.title, 'Persist')
        self.assertEqual(db_msg.content, 'Persist test')

    def test_create_notification_multiple_types(self):
        """Should work for all message types."""
        for msg_type in Message.MessageType.values:
            msg = create_notification(
                receiver=self.receiver,
                type=msg_type,
                title=f'Type {msg_type}',
                content=f'Content for {msg_type}',
            )
            self.assertEqual(msg.type, msg_type)

    def test_create_notification_default_related_fields(self):
        """related_type and related_id should default to empty/null."""
        msg = create_notification(
            receiver=self.receiver,
            type=Message.MessageType.SYSTEM,
            title='Defaults',
            content='Test defaults',
        )
        self.assertEqual(msg.related_type, '')
        self.assertIsNone(msg.related_id)
