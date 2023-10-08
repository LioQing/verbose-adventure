from django.urls import path
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r"user", views.UserView)
router.register(r"adventure", views.AdventureView)
router.register(r"scene", views.SceneView)

user_urlpatterns = [
    path(
        "user-utils/whitelist/",
        views.WhitelistView.as_view(),
        name="whitelist",
    ),
    path(
        "user-utils/unwhitelist/",
        views.UnwhitelistView.as_view(),
        name="unwhitelist",
    ),
    path(
        "user-utils/me/",
        views.UserMeView.as_view(),
        name="user-me",
    ),
    path(
        "user-utils/details/<int:id>/",
        views.UserDetailsView.as_view(),
        name="user-details",
    ),
]

convo_urlpatterns = [
    path(
        "convo/start/<int:id>/",
        views.ConvoStartView.as_view(),
        name="convo-start",
    ),
    path(
        "convo/respond/<int:id>/",
        views.ConvoRespondView.as_view(),
        name="convo-respond",
    ),
    path(
        "convo/history/<int:id>/",
        views.ConvoHistoryView.as_view(),
        name="convo-history",
    ),
    path(
        "convo/summary/<int:id>/",
        views.ConvoSummaryView.as_view(),
        name="convo-summary",
    ),
    path(
        "convo/token-count/<int:id>/",
        views.ConvoTokenCountView.as_view(),
        name="convo-token-count",
    ),
    path(
        "convo/token-count/",
        views.ConvoTotalTokenCountView.as_view(),
        name="convo-total-token-count",
    ),
]

scene_runner_urlpatterns = [
    path(
        "scene-runner/scene/<str:id>/",
        views.SceneRunnerSceneView.as_view(),
        name="scene-runner-scene",
    ),
    path(
        "scene-runner/create/<str:scene_id>/",
        views.SceneRunnerCreateView.as_view(),
        name="scene-runner-create",
    ),
    path(
        "scene-runner/respond/<int:runner_id>/<str:npc_id>/",
        views.SceneRunnerRespondView.as_view(),
        name="scene-runner-respond",
    ),
]

urlpatterns = [
    *router.urls,
    *user_urlpatterns,
    *convo_urlpatterns,
    *scene_runner_urlpatterns,
    path("ping", views.PingPongView.as_view(), name="ping"),
]
