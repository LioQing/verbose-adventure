from django.urls import path

from . import views

urlpatterns = [
    path(
        "login/", views.ObtainTokenPairView.as_view(), name="token-obtain-pair"
    ),
    path(
        "login/refresh/",
        views.TokenRefreshView.as_view(),
        name="token-refresh",
    ),
]
