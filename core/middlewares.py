import logging

from config.convo import convo_config


class RequestLogMiddleware:
    """Log the request"""

    logger: logging.Logger
    get_response: callable

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(convo_config.log_level)

    def __call__(self, request):
        """Log the request and response"""
        log_data = {
            "user": request.user.pk,
            "remote_address": request.META["REMOTE_ADDR"],
            "request_method": request.method,
            "request_path": request.get_full_path(),
            "request_body": request.body,
        }

        response = self.get_response(request)

        if response["content-type"] == "application/json":
            if getattr(response, "streaming", False):
                response_body = "<<<Streaming>>>"
            else:
                response_body = response.content
        else:
            response_body = "<<<Not JSON>>>"

        log_data = log_data | {
            "response_status": response.status_code,
            "response_body": response_body,
        }

        self.logger.debug("%s", log_data)

        return response
