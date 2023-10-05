from enum import StrEnum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_serializer


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
    required: bool = Field(False, exclude=True)

    @model_serializer
    def model_dump(self) -> Dict[str, Any]:
        """Dump the model"""
        dump = {"type": self.type, "description": self.description}

        if self.enum is not None:
            dump["enum"] = self.enum

        return dump


class Parameters(BaseModel):
    """Parameters for function"""

    parameters: Dict[str, Parameter]

    @model_serializer
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
    parameters: Parameters
    description: str


class FunctionCallRequest(BaseModel):
    """Function call for ChatCompletion.create"""

    auto: Optional[bool] = Field(False)
    name: Optional[str] = Field(None)

    @model_serializer
    def model_dump(self) -> Dict[str, Any] | str:
        """Dump the model"""
        if self.name is not None:
            return {"name": self.name}
        if self.auto:
            return "auto"

        return "none"


class FunctionCall(BaseModel):
    """Function call"""

    name: str
    arguments: str


class Message(BaseModel):
    """Message for conversation"""

    role: Role
    content: Optional[str] = Field(None)
    name: Optional[str] = Field(None)
    function_call: Optional[FunctionCall] = Field(None)

    @model_serializer
    def model_dump(self) -> Dict[str, Any]:
        """Dump the model"""
        dump = {"role": self.role, "content": self.content}

        if self.name is not None:
            dump["name"] = self.name

        if self.function_call is not None:
            dump["function_call"] = self.function_call

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
    functions: Optional[List[Function]] = Field(None)
    function_call: FunctionCallRequest = Field(
        default_factory=FunctionCallRequest
    )
    temperature: float = Field(1.0)
    top_p: float = Field(1.0)
    n: int = Field(1)
    max_tokens: int = Field(2000)

    def model_dump(self) -> Dict[str, Any]:
        """Dump the model"""
        dump = super().model_dump()

        if self.functions is None:
            dump.pop("functions")
            dump.pop("function_call")

        return dump
