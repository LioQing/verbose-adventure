from rest_framework_simplejwt import serializers as jwt_serializers


class TokenObtainPairSerializer(jwt_serializers.TokenObtainPairSerializer):
    """Serializer for ObtainTokenPairView"""

    pass
