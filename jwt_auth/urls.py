from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path(
        "login/", views.ObtainTokenPairView.as_view(), name="token-obtain-pair"
    ),
    path("login/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]
