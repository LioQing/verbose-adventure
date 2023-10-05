from enum import StrEnum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Role(StrEnum):
    """Role enumeration for conversation messages"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"

    def __repr__(self) -> str:
        """Get the string representation of the role"""
        return repr(self.value)


class Parameter(BaseModel):
    """Function parameter"""

    type: str
    description: str
    enum: Optional[List[str]] = Field(None)
    required: bool = Field(False)

    def model_dump(self) -> Dict[str, Any]:
        """Dump the model"""
        dump = super().model_dump()
        dump.pop("required")

        if self.enum is None:
            dump.pop("enum")

        return dump


class Parameters(BaseModel):
    """Parameters for function"""

    parameters: Dict[str, Parameter]

    def model_dump(self) -> Dict[str, Any]:
        """Dump the model"""
        dump = {
            "type": "object",
            "properties": {
                k: v.model_dump() for k, v in self.parameters.items()
            },
            "required": [
                k for k, v in self.parameters.items() if v.required is True
            ],
        }

        return dump


class Function(BaseModel):
    """Function"""

    name: str
    parameters: Dict[str, Parameter]
    description: str


class CreateFunctionCall(BaseModel):
    """Function call for ChatCompletion.create"""

    auto: bool = Field(False)
    name: str

    def model_dump(self) -> Dict[str, Any] | str:
        """Dump the model"""
        if self.auto:
            return "auto"

        return {"name": self.name}


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
    object: str
    created: int
    model: str
    choices: List[Choice]
    usage: Usage


class ChatcmplRequest(BaseModel):
    """Chat completition request body"""

    deployment_id: str
    model: str
    messages: List[Dict[str, Any]]
