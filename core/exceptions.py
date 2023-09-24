from rest_framework.exceptions import APIException


class AdventureStartedException(APIException):
    """Exception for when the adventure has already started."""

    status_code = 400
    default_detail = "Adventure has already started."
    default_code = "adventure_started"
