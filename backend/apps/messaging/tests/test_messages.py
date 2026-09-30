from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.conversations.models import (
    Conversation,
    ConversationMember,
)
from apps.messaging.models import Message, MessageRead


User = get_user_model()


class MessageTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="password123",
        )

        self.other_user = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="password123",
        )

        self.outsider = User.objects.create_user(
            username="outsider",
            email="outsider@example.com",
            password="password123",
        )

        self.conversation = Conversation.objects.create(
            type=Conversation.TypeChoices.GROUP,
            title="Test Group",
        )

        ConversationMember.objects.create(
            conversation=self.conversation,
            user=self.user,
            role=ConversationMember.RoleChoices.OWNER,
        )

        ConversationMember.objects.create(
            conversation=self.conversation,
            user=self.other_user,
            role=ConversationMember.RoleChoices.MEMBER,
        )

        self.message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user,
            text="Hello",
        )
    
    def test_messages_require_authentication(self):
        response = self.client.get(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/messages/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
    
    def test_member_can_list_messages(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/messages/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_non_member_cannot_list_messages(self):
        self.client.force_authenticate(user=self.outsider)

        response = self.client.get(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/messages/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
    
    def test_member_can_create_message(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/messages/",
            {
                "text": "Hello from member",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["sender"],
            self.other_user.id,
        )

        self.assertEqual(
            response.data["conversation"],
            self.conversation.id,
        )

    def test_non_member_cannot_create_message(self):
        self.client.force_authenticate(user=self.outsider)

        response = self.client.post(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/messages/",
            {
                "text": "I should not be here",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        
    def test_sender_can_update_message(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/messages/"
            f"{self.message.id}/",
            {
                "text": "Updated",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.message.refresh_from_db()

        self.assertEqual(
            self.message.text,
            "Updated",
        )
        
    def test_other_user_cannot_update_message(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/messages/"
            f"{self.message.id}/",
            {
                "text": "Hacked",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        
    def test_sender_can_soft_delete_message(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/messages/"
            f"{self.message.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.message.refresh_from_db()

        self.assertTrue(self.message.is_deleted)
        
        self.assertTrue(
            Message.objects.filter(
                id=self.message.id
            ).exists()
        )

    def test_other_user_cannot_delete_message(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.delete(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/messages/"
            f"{self.message.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.message.refresh_from_db()

        self.assertFalse(self.message.is_deleted)        
        
    def test_deleted_message_cannot_be_edited(self):
        self.message.is_deleted = True
        self.message.save()

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/messages/"
            f"{self.message.id}/",
            {
                "text": "New text",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.message.refresh_from_db()

        self.assertEqual(
            self.message.text,
            "Hello",
        )

    def test_deleted_message_returns_empty_text(self):
        self.message.is_deleted = True
        self.message.save()

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/messages/"
            f"{self.message.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["text"],
            "",
        )

        self.assertTrue(
            response.data["is_deleted"]
        )


    def test_member_can_mark_message_as_read(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/messages/"
            f"{self.message.id}/read/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            MessageRead.objects.filter(
                message=self.message,
                user=self.other_user,
            ).exists()
        )
        
    def test_marking_message_as_read_twice_does_not_create_duplicate(self):
        self.client.force_authenticate(user=self.other_user)

        url = (
            f"/api/v1/conversations/"
            f"{self.conversation.id}/messages/"
            f"{self.message.id}/read/"
        )

        first_response = self.client.post(url)
        second_response = self.client.post(url)

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            MessageRead.objects.filter(
                message=self.message,
                user=self.other_user,
            ).count(),
            1,
        )

    def test_user_cannot_mark_own_message_as_read(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/messages/"
            f"{self.message.id}/read/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_cannot_mark_message_from_another_conversation_as_read(self):
        another_conversation = Conversation.objects.create(
            type=Conversation.TypeChoices.GROUP,
            title="Another Group",
        )

        another_message = Message.objects.create(
            conversation=another_conversation,
            sender=self.user,
            text="Another message",
        )

        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/messages/"
            f"{another_message.id}/read/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )