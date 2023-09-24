from django.urls import path
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r"user", views.UserView)
router.register(r"adventure", views.AdventureView)

convo_urlpatterns = [
    path(
        "convo/<int:id>/start",
        views.ConvoStartView.as_view(),
        name="convo-start",
    ),
    path(
        "convo/<int:id>/respond",
        views.ConvoRespondView.as_view(),
        name="convo-respond",
    ),
    path(
        "convo/<int:id>/summary",
        views.ConvoSummaryView.as_view(),
        name="convo-summary",
    ),
    path(
        "convo/<int:id>/token-count",
        views.ConvoTokenCountView.as_view(),
        name="convo-token-count",
    ),
    path(
        "convo/token-count",
        views.ConvoTotalTokenCountView.as_view(),
        name="convo-total-token-count",
    ),
]

urlpatterns = [
    *router.urls,
    *convo_urlpatterns,
    path("ping", views.PingPongView.as_view(), name="ping"),
]
