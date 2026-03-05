import os

from haystack import component, Pipeline
from haystack.components.tools import ToolInvoker
from haystack_integrations.components.generators.google_genai import GoogleGenAIChatGenerator
from haystack.components.routers import ConditionalRouter
from haystack.components.websearch import SerperDevWebSearch
from haystack.core.component.types import Variadic
from haystack.dataclasses import ChatMessage
from haystack.tools import ComponentTool
from haystack.utils import Secret

from typing import Any, List, Dict

from dotenv import load_dotenv

load_dotenv(".env")

MODEL_ID="gemini-2.5-flash"

# TODO: Read about `unsafe` ConditionalRouter(routes, unsafe=True)
# TODO: Read about `Variadic`: messages: Variadic[List[ChatMessage]]

## helper component to temporarily store last user query before tool call
@component
class MessageCollector:

    def __init__(self):
        self._messages = []
    
    @component.output_types(messages=List[ChatMessage])
    def run(self, messages: Variadic[List[ChatMessage]]) -> Dict[str, Any]:
        self._messages.extend([msg for inner in messages for msg in inner])
        return {"messages": self._messages}
    
    def clear(self):
        self._messages = []


# Create a tool from a component
web_tool = ComponentTool(component=SerperDevWebSearch(api_key=Secret.from_env_var("SERPERDEV_API_KEY"), top_k=3))

# Define routing conditions
routes = [
    {
        "condition": "{{replies[0].tool_calls | length > 0}}",
        "output": "{{replies}}",
        "output_name": "there_are_tool_calls",
        "output_type": List[ChatMessage],
    },
    {
        "condition": "{{replies[0].tool_calls | length == 0}}",
        "output": "{{replies}}",
        "output_name": "final_replies",
        "output_type": List[ChatMessage],
    },
]

# Create the Pipeline
tool_agent = Pipeline()

tool_agent.add_component("message_collector", MessageCollector())
tool_agent.add_component(
    "generator", GoogleGenAIChatGenerator(model=MODEL_ID, tools=[web_tool]),
)
tool_agent.add_component("router", ConditionalRouter(routes, unsafe=True))
tool_agent.add_component("tool_invoker", ToolInvoker(tools=[web_tool]))

tool_agent.connect("generator.replies", "router")
tool_agent.connect("router.there_are_tool_calls", "tool_invoker")
tool_agent.connect("router.there_are_tool_calls", "message_collector")
tool_agent.connect("tool_invoker.tool_messages", "message_collector")
tool_agent.connect("message_collector", "generator.messages")

messages = [
    ChatMessage.from_system(
        "You are a helpful agent choosing the right tool when necessary.",
    ),
    ChatMessage.from_user(
        "How is the Weather in Bucharest?",
    ),
]

result = tool_agent.run({"messages": messages})

print(f"result: {result}")

print(result["router"]["final_replies"][0].text)