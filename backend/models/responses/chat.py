from pydantic import BaseModel


class LLMChatResponse(BaseModel):
    response: str