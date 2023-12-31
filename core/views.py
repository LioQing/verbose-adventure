import logging

from rest_framework import exceptions as rest_exceptions
from rest_framework import generics, permissions, response, views, viewsets

from config.convo import convo_config
from engine import models as engine_models
from engine.convo import Convo
from engine.scene import Scene
from rest_auth.permissions import IsWhitelisted

from . import exceptions, models, serializers
from .couplers.convo import ConvoCoupler
from .couplers.scene import SceneCoupler


class UserView(
    generics.CreateAPIView,
    generics.RetrieveAPIView,
    generics.ListAPIView,
    generics.DestroyAPIView,
    generics.UpdateAPIView,
    viewsets.GenericViewSet,
):
    """Viewset for the User model"""

    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer: serializers.UserSerializer):
        """Create the user"""
        user: models.User = serializer.save()
        user.set_password(user.password)
        user.save()

    def perform_update(self, serializer: serializers.UserSerializer):
        """Update the user"""
        user = serializer.save()

        if serializer.validated_data.get("password"):
            user.set_password(user.password)
            user.save()


class UserMeView(views.APIView):
    """View for getting the logged in user using token"""

    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Return the logged in user"""
        serializer = self.serializer_class(request.user)
        return response.Response(serializer.data)


class UserDetailsView(views.APIView):
    """View for getting the user details"""

    serializer_class = serializers.UserDetailsSerializer
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, id, *args, **kwargs):
        """Return the user details"""
        logger = logging.getLogger(__name__)
        logger.setLevel(convo_config.log_level)

        try:
            user = models.User.objects.get(id=id)
            adventures = models.Adventure.objects.filter(
                user=user, scenenpcadventurepair=None
            )
            scene_runners = models.SceneRunner.objects.filter(user=user)
            scene_npcs = models.SceneNpcAdventurePair.objects.filter(
                runner__in=scene_runners
            )
            serializer = self.serializer_class(
                {
                    "num_adventures": len(adventures),
                    "token_count": sum(a.token_count for a in adventures)
                    + sum(n.token_count for n in scene_npcs),
                    "adventures": [
                        {"id": a.id, "token_count": a.token_count}
                        for a in adventures
                    ],
                    "scenes": [
                        {
                            "id": s.id,
                            "name": s.scene.name,
                            "npcs": [
                                {
                                    "index": n.npc.index,
                                    "name": n.npc.name,
                                    "title": n.npc.title,
                                    "token_count": n.token_count,
                                }
                                for n in scene_npcs
                                if n.runner == s
                            ],
                            "token_count": sum(
                                n.token_count
                                for n in scene_npcs
                                if n.runner == s
                            ),
                        }
                        for s in scene_runners
                    ],
                }
            )
            logger.debug("serializer: %s", serializer)
            return response.Response(serializer.data)
        except Exception as e:
            import traceback

            traceback.print_exc()
            logger.error(e)
            raise


class WhitelistView(generics.CreateAPIView, views.APIView):
    """View for whitelisting a user"""

    serializer_class = serializers.WhitelistSerializer
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        """Whitelist the user"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            username = serializer.validated_data["username"]
            user = models.User.objects.get(username=username)
            user.is_whitelisted = True
            user.save()
            return response.Response(serializer.data)
        except Exception as e:
            import traceback

            traceback.print_exc()
            logger = logging.getLogger(__name__)
            logger.error(e)
            raise e


class UnwhitelistView(generics.CreateAPIView, views.APIView):
    """View for unwhitelisting a user"""

    serializer_class = serializers.WhitelistSerializer
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        """Whitelist the user"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            username = serializer.validated_data["username"]
            user = models.User.objects.get(username=username)
            user.is_whitelisted = False
            user.save()
            return response.Response(serializer.data)
        except Exception as e:
            import traceback

            traceback.print_exc()
            logger = logging.getLogger(__name__)
            logger.error(e)
            raise e


class PingPongView(views.APIView):
    """View for checking if the server is running"""

    serializer_class = serializers.PingPongSerializer
    permission_classes = [IsWhitelisted]

    def get(self, request):
        """Return a pong response"""
        serializer = self.serializer_class(data={"ping": "pong"})
        serializer.is_valid(raise_exception=True)
        return response.Response(serializer.data)


class AdventureView(
    generics.CreateAPIView,
    generics.RetrieveAPIView,
    generics.ListAPIView,
    generics.UpdateAPIView,
    viewsets.GenericViewSet,
):
    """View for the adventure"""

    queryset = models.Adventure.objects.all()
    permission_classes = [IsWhitelisted]

    def get_serializer_class(self):
        """Return the serializer class"""
        if self.action in ["create", "update", "partial_update"]:
            return serializers.AdventureOwnedSerializer
        return serializers.AdventureSerializer

    def get_queryset(self):
        """Return the queryset"""
        if self.action in ["create", "update", "partial_update"]:
            return models.Adventure.objects.filter(user=self.request.user)
        return models.Adventure.objects.all()

    def perform_create(self, serializer):
        """Create the adventure"""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Update the adventure"""
        serializer.save(user=self.request.user)


class ConvoHistoryView(views.APIView):
    """View for the adventure convo history"""

    serializer_class = serializers.ConvoHistorySerializer
    permission_classes = [IsWhitelisted]

    def get(self, request, id, *args, **kwargs):
        """Return the convo history"""
        logger = logging.getLogger(__name__)
        logger.setLevel(convo_config.log_level)

        try:
            adventure = models.Adventure.objects.get(id=id)

            if adventure.user != request.user:
                raise exceptions.AdventureNotOwnedByUserException()

            length = (
                self.request.query_params.get("username")
                or convo_config.history_length
            )

            messages = models.Message.objects.get_latest_n_messages(
                adventure, length
            )
            serializer = self.serializer_class({"history": messages})
            logger.debug("serializer: %s", serializer)
            return response.Response(serializer.data)
        except Exception as e:
            import traceback

            traceback.print_exc()
            logger.error(e)
            raise e


class ConvoStartView(generics.CreateAPIView, views.APIView):
    """View for initializing the adventure convo"""

    serializer_class = serializers.ConvoStartSerializer
    permission_classes = [IsWhitelisted]

    def create(self, request, id, *args, **kwargs):
        """Return first API response of the adventure"""
        logger = logging.getLogger(__name__)
        logger.setLevel(convo_config.log_level)

        try:
            adventure = models.Adventure.objects.get(id=id)

            if adventure.user != request.user:
                raise exceptions.AdventureNotOwnedByUserException()

            # Validate this is the first call
            if adventure.iteration != 0:
                raise exceptions.AdventureStartedException()

            convo_coupler = ConvoCoupler(adventure)
            convo = Convo(convo_coupler)

            init_message = convo.init_story()
            logger.debug("init_message: %s", init_message)
            init_response = init_message.content

            serializer = self.get_serializer({"response": init_response})
            logger.debug("serializer: %s", serializer)
            return response.Response(serializer.data)
        except Exception as e:
            import traceback

            traceback.print_exc()
            logger.error(e)
            raise e


class ConvoRespondView(generics.CreateAPIView, views.APIView):
    """View for user responding to the adventure convo"""

    serializer_class = serializers.ConvoRespondSerializer
    permission_classes = [IsWhitelisted]

    def create(self, request, id, *args, **kwargs):
        """Return API response of the adventure"""
        logger = logging.getLogger(__name__)
        logger.setLevel(convo_config.log_level)

        try:
            adventure = models.Adventure.objects.get(id=id)

            if adventure.user != request.user:
                raise exceptions.AdventureNotOwnedByUserException()

            convo_coupler = ConvoCoupler(adventure)
            convo = Convo(convo_coupler)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_response = serializer.validated_data["user_response"]
            user_message = engine_models.Message(
                role=engine_models.Role.USER,
                content=user_response,
            )
            user_message = convo.process_user_response(user_message)
            logger.debug("user_message: %s", user_message)

            api_response = convo.process_api_response()
            logger.debug("api_response: %s", api_response)

            summary_message = convo.summarize()
            logger.debug("summary_message: %s", summary_message)

            serializer = self.serializer_class(
                {
                    "user_response": user_message.content,
                    "api_response": api_response.content,
                    "summary": summary_message.content
                    if summary_message
                    else None,
                }
            )
            logger.debug("serializer: %s", serializer)
            return response.Response(serializer.data)
        except Exception as e:
            import traceback

            traceback.print_exc()
            logger.error(e)
            raise e


class ConvoSummaryView(views.APIView):
    """View for getting the adventure convo summary"""

    serializer_class = serializers.ConvoSummarySerializer
    permission_classes = [IsWhitelisted]

    def get(self, request, id, *args, **kwargs):
        """Return summary of the adventure convo"""
        logger = logging.getLogger(__name__)
        logger.setLevel(convo_config.log_level)

        try:
            adventure = models.Adventure.objects.get(id=id)

            if adventure.summary is None:
                raise exceptions.AdventureSummaryNotFoundException()

            serializer = self.serializer_class(
                {"summary": adventure.summary.summary}
            )
            logger.debug("serializer: %s", serializer)
            return response.Response(serializer.data)
        except Exception as e:
            import traceback

            traceback.print_exc()
            logger.error(e)
            raise e


class ConvoTokenCountView(views.APIView):
    """View for getting the adventure convo token count"""

    serializer_class = serializers.ConvoTokenCountSerializer
    permission_classes = [IsWhitelisted]

    def get(self, request, id, *args, **kwargs):
        """Return token count of the adventure convo"""
        logger = logging.getLogger(__name__)
        logger.setLevel(convo_config.log_level)

        try:
            adventure = models.Adventure.objects.get(id=id)
            token_count = adventure.token_count

            serializer = self.serializer_class({"token_count": token_count})
            logger.debug("serializer: %s", serializer)
            return response.Response(serializer.data)
        except Exception as e:
            import traceback

            traceback.print_exc()
            logger.error(e)
            raise e


class ConvoTotalTokenCountView(views.APIView):
    """View for getting the adventure convo total token count"""

    serializer_class = serializers.ConvoTokenCountSerializer
    permission_classes = [IsWhitelisted]

    def get(self, request, *args, **kwargs):
        """Return token count of the adventure convo"""
        logger = logging.getLogger(__name__)
        logger.setLevel(convo_config.log_level)

        try:
            adventure = models.Adventure.objects.all()
            token_count = sum(a.token_count for a in adventure)

            serializer = self.serializer_class({"token_count": token_count})
            logger.debug("serializer: %s", serializer)
            return response.Response(serializer.data)
        except Exception as e:
            import traceback

            traceback.print_exc()
            logger.error(e)
            raise e


class SceneView(
    generics.RetrieveAPIView,
    generics.ListAPIView,
    viewsets.GenericViewSet,
):
    """View for the Scene model"""

    queryset = models.Scene.objects.all()
    serializer_class = serializers.SceneSerializer
    permission_classes = [IsWhitelisted]


class SceneRunnerCreateView(generics.CreateAPIView, views.APIView):
    """View for creating the scene runner"""

    serializer_class = serializers.SceneRunnerCreateSerializer
    permission_classes = [IsWhitelisted]

    def create(self, request, scene_id: str, *args, **kwargs):
        """Return the scene runner"""
        logger = logging.getLogger(__name__)
        logger.setLevel(convo_config.log_level)

        try:
            try:
                scene = models.Scene.objects.get(id=scene_id)
            except models.Scene.DoesNotExist:
                raise rest_exceptions.NotFound(f"Scene {scene_id} not found")

            scene_runner = models.SceneRunner.objects.create(
                user=request.user, scene=scene
            )

            scene_coupler = SceneCoupler(scene_runner)
            scene_data = scene.to_scene_data()
            engine_scene = Scene(
                scene_coupler,
                scene_data,
            )

            engine_scene.init_scene()

            serializer = self.serializer_class({"id": scene_runner.id})
            logger.debug("serializer: %s", serializer)
            return response.Response(serializer.data)
        except Exception as e:
            import traceback

            traceback.print_exc()
            logger.error(e)
            raise e


class SceneRunnerRespondView(generics.CreateAPIView, views.APIView):
    """View for user responding to the scene"""

    serializer_class = serializers.ConvoRespondSerializer
    permission_classes = [IsWhitelisted]

    def create(self, request, runner_id: int, npc_id: str, *args, **kwargs):
        """Return API response of the scene"""
        logger = logging.getLogger(__name__)
        logger.setLevel(convo_config.log_level)

        try:
            try:
                runner = models.SceneRunner.objects.get(id=runner_id)
            except models.SceneRunner.DoesNotExist:
                raise rest_exceptions.NotFound(
                    f"SceneRunner {runner_id} not found"
                )

            if runner.user != request.user:
                raise exceptions.SceneRunnerNotOwnedByUserException()

            try:
                npc = models.SceneNpc.objects.get(id=npc_id)
            except models.SceneNpc.DoesNotExist:
                raise rest_exceptions.NotFound(f"SceneNpc {npc_id} not found")

            scene_coupler = SceneCoupler(runner)
            scene = Scene(scene_coupler, runner.scene.to_scene_data())

            convo_coupler = scene.process_user_selection(npc.index)
            if convo_coupler is None:
                logger.error("Unreachable reached, convo coupler is None")
                raise rest_exceptions.APIException(
                    "Unreachable reached, convo coupler is None"
                )

            convo = Convo(convo_coupler)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_response = serializer.validated_data["user_response"]
            user_message = engine_models.Message(
                role=engine_models.Role.USER,
                content=user_response,
            )
            user_message = convo.process_user_response(user_message)
            logger.debug("user_message: %s", user_message)

            api_response = convo.process_api_response()
            logger.debug("api_response: %s", api_response)

            summary_message = convo.summarize()
            logger.debug("summary_message: %s", summary_message)

            serializer = self.serializer_class(
                {
                    "user_response": user_message.content,
                    "api_response": api_response.content,
                    "summary": summary_message.content
                    if summary_message
                    else None,
                }
            )
            logger.debug("serializer: %s", serializer)
            return response.Response(serializer.data)
        except Exception as e:
            import traceback

            traceback.print_exc()
            logger.error(e)
            raise e


class SceneRunnerSceneView(views.APIView):
    """View for getting the scene runner scene"""

    serializer_class = serializers.SceneSerializer
    permission_classes = [IsWhitelisted]

    def get(self, request, id: str, *args, **kwargs):
        """Return the scene runner scene"""
        logger = logging.getLogger(__name__)
        logger.setLevel(convo_config.log_level)

        try:
            try:
                runner = models.SceneRunner.objects.get(id=id)
            except models.SceneRunner.DoesNotExist:
                raise rest_exceptions.NotFound(f"SceneRunner {id} not found")

            if runner.user != request.user:
                raise exceptions.SceneRunnerNotOwnedByUserException()

            serializer = self.serializer_class(runner.scene)
            logger.debug("serializer: %s", serializer)
            return response.Response(serializer.data)
        except Exception as e:
            import traceback

            traceback.print_exc()
            logger.error(e)
            raise e
