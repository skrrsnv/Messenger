import secrets

from django.conf import settings
from rest_framework.permissions import BasePermission


class HasInternalAPIToken(BasePermission):
    def has_permission(self, request, view):
        expected_token = settings.INTERNAL_API_TOKEN
        provided_token = request.headers.get(
            "X-Internal-Token",
            "",
        )

        return bool(
            expected_token
            and provided_token
            and secrets.compare_digest(
                expected_token,
                provided_token,
            )
        )