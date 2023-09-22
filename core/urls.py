from django.urls import path
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r"user", views.UserView)
router.register(r"modify-user", views.ModifyUserView)

urlpatterns = [
    *router.urls,
    path("ping/", views.PingPongView.as_view(), name="ping"),
]
