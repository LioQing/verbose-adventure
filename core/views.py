import logging

from rest_framework import generics, permissions, response, views, viewsets

from engine import models as engine_models
from engine.convo import Convo
from rest_auth.permissions import IsAdventureUser, IsWhitelisted

from . import exceptions, models, serializers
from .convo_coupler import ConvoCoupler


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
    serializer_class = serializers.AdventureSerializer
    permission_classes = [IsWhitelisted]


class ConvoStartView(
    generics.CreateAPIView,
    views.APIView,
):
    """View for initializing the adventure convo"""

    serializer_class = serializers.ConvoStartSerializer
    permission_classes = [IsWhitelisted]

    def create(self, request, id, *args, **kwargs):
        """Return first API response of the adventure"""
        logger = logging.getLogger(__name__)
        logger.debug("request:", request)

        try:
            adventure = models.Adventure.objects.get(id=id)

            # Validate this is the first call
            if adventure.iteration != 0:
                raise exceptions.AdventureStartedException()

            convo_coupler = ConvoCoupler(adventure)
            convo = Convo(convo_coupler)

            init_message = convo.init_story()
            logger.debug("init_message:", init_message)
            init_response = init_message.content

            serializer = self.get_serializer({"response": init_response})
            logger.debug("serializer:", serializer)
            return response.Response(serializer.data)
        except Exception as e:
            import traceback

            traceback.print_exc()
            logger.error(e)
            raise e


class ConvoRespondView(
    generics.CreateAPIView,
    views.APIView,
):
    """View for user responding to the adventure convo"""

    serializer_class = serializers.ConvoRespondSerializer
    permission_classes = [IsAdventureUser]

    def create(self, request, id, *args, **kwargs):
        """Return API response of the adventure"""
        logger = logging.getLogger(__name__)
        logger.debug("request:", request)

        adventure = models.Adventure.objects.get(id=id)
        convo_coupler = ConvoCoupler(adventure)
        convo = Convo(convo_coupler)

        user_response: str = request.data["user_response"]
        user_message = engine_models.Message(
            role=engine_models.Role.USER,
            content=user_response,
        )
        user_message = convo.process_user_response(user_message)
        logger.debug("user_message:", user_message)

        api_response = convo.process_api_response()
        logger.debug("api_response:", api_response)

        summary_message = convo.summarize()
        logger.debug("summary_message:", summary_message)

        serializer = self.get_serializer(
            {
                "user_response": user_response,
                "api_response": api_response.content,
                "summary": summary_message.content
                if summary_message
                else None,
            }
        )
        return response.Response(serializer.data)
