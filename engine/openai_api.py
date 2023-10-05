import logging
from typing import List

import openai

from config.logger import logger_config
from config.openai import open_ai_config

from .models import (
    Chatcmpl,
    ChatcmplRequest,
    Function,
    FunctionCallRequest,
    Message,
)

openai.api_key = open_ai_config.key
openai.api_base = open_ai_config.url
openai.api_type = open_ai_config.api_type
openai.api_version = open_ai_config.version


logger = logging.getLogger(__name__)
logger.setLevel(logger_config.level)


def call_api(messages: List[Message]) -> Chatcmpl:
    """Call the OpenAI API with the given messages"""
    request = ChatcmplRequest(
        deployment_id=open_ai_config.deployment,
        model=open_ai_config.model,
        messages=[m.model_dump() for m in messages],
    )
    request = request.model_dump()

    logger.debug(f"Calling API with messages: {request}")

    response = openai.ChatCompletion.create(**request)
    response = Chatcmpl(**response)

    logger.debug(f"API response: {response}")
    return response


def call_api_function(messages: List[Message], function: Function) -> Chatcmpl:
    """Call the OpenAI API to provide arguments for the function"""
    request = ChatcmplRequest(
        deployment_id=open_ai_config.deployment,
        model=open_ai_config.model,
        messages=[m.model_dump() for m in messages],
        functions=[function],
        function_call=FunctionCallRequest(name=function.name),
    )
    request = request.model_dump()

    logger.debug(f"Calling API with messages and function: {request}")

    response = openai.ChatCompletion.create(**request)
    response = Chatcmpl(**response)

    logger.debug(f"API response: {response}")
    return response
