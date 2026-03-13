from pydantic import BaseModel, Field
from typing import Optional, Literal
from models.roles.chat_roles import ChatRoles


class ChatMessage(BaseModel):
    role: Literal[ChatRoles.USER, ChatRoles.ASSISTANT, ChatRoles.SYSTEM]
    text: str
    input_tokens: Optional[int] = Field(default=None)
    output_tokens: Optional[int] = Field(default=None)
