from enum import StrEnum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class Role(StrEnum):
    """Role enumeration for conversation messages"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class FunctionCall(BaseModel):
    """Function call"""

    name: str
    arguments: str


class Message(BaseModel):
    """Message for conversation"""

    role: Role
    content: str
    name: Optional[str] = Field(None)
    function_call: Optional[FunctionCall] = Field(None)

    def model_dump(self) -> Dict[str, Any]:
        """Dump the model"""
        dump = super().model_dump()
        if self.name is None:
            dump.pop("name")
        if self.function_call is None:
            dump.pop("function_call")

        return dump


class Choice(BaseModel):
    """Message choice by OpenAI API"""

    index: int
    message: Message
    finish_reason: str


class Usage(BaseModel):
    """Usage by OpenAI API"""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class Chatcmpl(BaseModel):
    """Chat completion by OpenAI API"""

    id: str
    object_name: str
    created_at: str
    model: str
    choices: Dict[str, Choice]
    usage: Usage


class ChatcmplRequest(BaseModel):
    """Chat completition request body"""

    deployment_id: str
    model: str
    messages: Dict[str, Message]
