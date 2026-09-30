from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AuthenticationTests(APITestCase):

    def test_register_user(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "username": "testuser",
                "email": "test@example.com",
                "password": "strongpassword123",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            User.objects.filter(username="testuser").exists()
        )

    def test_register_invalid_password(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "username": "testuser",
                "email": "test@example.com",
                "password": "123",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_login(self):
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="strongpassword123",
        )

        response = self.client.post(
            "/api/v1/auth/login/",
            {
                "username": "testuser",
                "password": "strongpassword123",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials(self):
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="strongpassword123",
        )

        response = self.client.post(
            "/api/v1/auth/login/",
            {
                "username": "testuser",
                "password": "wrongpassword",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_me_requires_authentication(self):
        response = self.client.get(
            "/api/v1/auth/me/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_me_authenticated(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="strongpassword123",
        )

        self.client.force_authenticate(user=user)

        response = self.client.get(
            "/api/v1/auth/me/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")