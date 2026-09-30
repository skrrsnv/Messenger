from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.conversations.models import (
    Conversation,
    ConversationMember,
)


User = get_user_model()


class ConversationMembershipTests(APITestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="password123",
        )

        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="password123",
        )

        self.member = User.objects.create_user(
            username="member",
            email="member@example.com",
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
            user=self.owner,
            role=ConversationMember.RoleChoices.OWNER,
        )

        ConversationMember.objects.create(
            conversation=self.conversation,
            user=self.admin,
            role=ConversationMember.RoleChoices.ADMIN,
        )

        ConversationMember.objects.create(
            conversation=self.conversation,
            user=self.member,
            role=ConversationMember.RoleChoices.MEMBER,
        )

    def test_member_can_list_members(self):
        self.client.force_authenticate(user=self.member)

        response = self.client.get(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/members/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_member_cannot_list_members(self):
        self.client.force_authenticate(user=self.outsider)

        response = self.client.get(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/members/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_member_cannot_add_member(self):
        self.client.force_authenticate(user=self.member)

        response = self.client.post(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/members/",
            {
                "user": self.outsider.id,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_admin_can_add_member(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/members/",
            {
                "user": self.outsider.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_owner_can_add_member(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/members/",
            {
                "user": self.outsider.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_admin_can_remove_member(self):
        self.client.force_authenticate(user=self.admin)

        membership = ConversationMember.objects.get(
            conversation=self.conversation,
            user=self.member,
        )

        response = self.client.delete(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/members/"
            f"{membership.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

    def test_admin_cannot_remove_admin(self):
        self.client.force_authenticate(user=self.admin)

        owner_membership = ConversationMember.objects.get(
            conversation=self.conversation,
            user=self.owner,
        )

        response = self.client.delete(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/members/"
            f"{owner_membership.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_owner_can_remove_admin(self):
        self.client.force_authenticate(user=self.owner)

        admin_membership = ConversationMember.objects.get(
            conversation=self.conversation,
            user=self.admin,
        )

        response = self.client.delete(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/members/"
            f"{admin_membership.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

    def test_member_cannot_change_role(self):
        self.client.force_authenticate(user=self.member)

        member_membership = ConversationMember.objects.get(
            conversation=self.conversation,
            user=self.member,
        )

        response = self.client.patch(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/members/"
            f"{member_membership.id}/",
            {
                "role": ConversationMember.RoleChoices.ADMIN,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_owner_can_change_member_role(self):
        self.client.force_authenticate(user=self.owner)

        member_membership = ConversationMember.objects.get(
            conversation=self.conversation,
            user=self.member,
        )

        response = self.client.patch(
            f"/api/v1/conversations/"
            f"{self.conversation.id}/members/"
            f"{member_membership.id}/",
            {
                "role": ConversationMember.RoleChoices.ADMIN,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)