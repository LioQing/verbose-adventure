from django.apps import AppConfig


class JwtAuthConfig(AppConfig):
    """JWT Auth config"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "jwt_auth"
