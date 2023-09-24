from rest_framework import exceptions


class AdventureStartedException(exceptions.APIException):
    """Exception for when the adventure has already started."""

    status_code = 400
    default_detail = "Adventure has already started."
    default_code = "adventure_started"


class AdventureNotOwnedByUserException(exceptions.APIException):
    """Exception for when the adventure is not owned by the user."""

    status_code = 400
    default_detail = "Adventure is not owned by the user."
    default_code = "adventure_not_owned_by_user"


class AdventureSummaryNotFoundException(exceptions.NotFound):
    """Exception for when the adventure summary is not found."""

    status_code = 404
    default_detail = "Adventure summary not found."
    default_code = "adventure_summary_not_found"
