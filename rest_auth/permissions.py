from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from core.models import User


class IsWhitelisted(BasePermission):
    """Allow access only to whitelisted users."""

    def has_permission(self, request: Request, view):
        """Check if user is whitelisted."""
        user: User = request.user
        return user.is_authenticated and user.is_whitelisted
