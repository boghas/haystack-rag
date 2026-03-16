import os

from haystack.components.generators.chat import OpenAIChatGenerator
from haystack_integrations.components.generators.amazon_bedrock import AmazonBedrockChatGenerator
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore
from haystack.dataclasses import ChatMessage
from haystack.tools.tool import Tool
from haystack.tools.component_tool import ComponentTool
from haystack.components.agents import Agent
from haystack.utils import Secret
from haystack.components.websearch import SerperDevWebSearch
from haystack_integrations.components.generators.google_genai import GoogleGenAIChatGenerator
from typing import List, Dict
from utils.config import MODEL_ID
from components.rag import HybridRAGComponent
from typing import Callable

from dotenv import load_dotenv

load_dotenv(".env")

class HaystackAgent:

    def __init__(
            self,
            document_store: InMemoryDocumentStore | OpenSearchDocumentStore | None = None,
        ):
        self.document_store = document_store
        self._set_tools()
        self._create_agent()
    
    def _set_tools(self):
        web_search_tool = ComponentTool(
            component=SerperDevWebSearch(top_k=3, api_key=Secret.from_env_var("SERPERDEV_API_KEY")),
            name="web_tool",
            description="Tool to search the web for extra information.",
        )

        rag_tool = ComponentTool(
            component=HybridRAGComponent(document_store=self.document_store),
            name="rag_tool",
            description="Tool to search for internal data."
        )

        self.tools = [web_search_tool, rag_tool]
    
    def _create_agent(self):
        self.agent = Agent(
            chat_generator=GoogleGenAIChatGenerator(model=MODEL_ID),
            system_prompt="""You are a helpful assistant. When asked about internal data regarding security guides,
                use the `rag_tool` to search for relevant documents in the vector database and use those documents to answer the query.
                For any other query you must use the `web_tool` to search for external data from the web to form an answer.""",
            tools=self.tools
        )
    
    def run(self, query: str):
        message = ChatMessage.from_user(query)
        result = self.agent.run([message])

        return result["messages"][-1].text


