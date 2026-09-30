from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.conversations.models import (
    Conversation,
    ConversationMember,
)


User = get_user_model()


class ConversationTests(APITestCase):

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

    def test_conversation_list_requires_authentication(self):
        response = self.client.get(
            "/api/v1/conversations/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_member_can_list_conversations(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            "/api/v1/conversations/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_member_does_not_see_conversation(self):
        outsider = User.objects.create_user(
            username="outsider",
            email="outsider@example.com",
            password="password123",
        )

        self.client.force_authenticate(user=outsider)

        response = self.client.get(
            f"/api/v1/conversations/{self.conversation.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_member_can_retrieve_conversation(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f"/api/v1/conversations/{self.conversation.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_member_cannot_update_group(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            f"/api/v1/conversations/{self.conversation.id}/",
            {
                "title": "New title",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_owner_can_update_group(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            f"/api/v1/conversations/{self.conversation.id}/",
            {
                "title": "New title",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.conversation.refresh_from_db()

        self.assertEqual(
            self.conversation.title,
            "New title",
        )

    def test_member_cannot_delete_group(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.delete(
            f"/api/v1/conversations/{self.conversation.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_owner_can_delete_group(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            f"/api/v1/conversations/{self.conversation.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )