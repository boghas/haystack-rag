from enum import Enum


class ChatRoles(Enum):
    SYSTEM = "system_message"
    ASSISTANT = "assistant_message"
    USER = "user_message"