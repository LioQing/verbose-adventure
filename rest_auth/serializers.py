from rest_framework import serializers
from rest_framework_simplejwt import serializers as jwt_serializers


class TokenObtainPairSerializer(jwt_serializers.TokenObtainPairSerializer):
    """Serializer for ObtainTokenPairView"""

    pass


class TokenObtainPairResponseSerializer(serializers.Serializer):
    """Serializer for ObtainTokenPairView"""

    access = serializers.CharField()
    refresh = serializers.CharField()
