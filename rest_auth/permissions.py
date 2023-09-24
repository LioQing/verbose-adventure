from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from core.models import User


class IsWhitelisted(BasePermission):
    """Allow access only to whitelisted users."""

    def has_permission(self, request: Request, view) -> bool:
        """Check if user is whitelisted."""
        user: User = request.user
        return user.is_authenticated and user.is_whitelisted


class IsAdventureUser(BasePermission):
    """Allow access to only the adventure user."""

    def has_permission(self, request: Request, view) -> bool:
        """Check if user is the whitelisted user."""
        return IsWhitelisted().has_permission(request, view)

    def has_object_permission(self, request, view, obj) -> bool:
        """Check if user is the adventure user."""
        return (
            super().has_object_permission(request, view, obj)
            and obj.adventure.user == request.user
        )
