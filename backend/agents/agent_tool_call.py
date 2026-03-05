import os
from haystack.components.agents import Agent
from haystack_integrations.components.generators.google_genai import GoogleGenAIChatGenerator
from haystack.components.websearch import SerperDevWebSearch
from haystack.dataclasses import Document, ChatMessage
from haystack.tools.component_tool import ComponentTool
from haystack.utils import Secret
from haystack import component

from dotenv import load_dotenv

load_dotenv(".env")

SERPER_DEV_API_KEY = os.getenv("SERPERDEV_API_KEY", "")
MODEL_ID = "gemini-2.5-flash"

# TODO: What is the diff between haystack.Document and haystack.dataclasses.Document
# TODO: Convert Fahrenheit to Celsius with Tool

@component
class CelsiusFromFahrenheitConverterComponent:
    
    @component.output_types(temperature_in_celsius=int)
    def run(self, temperature_in_fahrenheit: int):
        temperature_in_celsius = (temperature_in_fahrenheit - 32) / 1.8

        print(f"Using the CelsiusFromFahrenheitConverterComponent...")

        return {
            "temperature_in_celsius": temperature_in_celsius
        }

# Web Search Component
web_search = SerperDevWebSearch(top_k=3, api_key=Secret.from_env_var("SERPERDEV_API_KEY"))

converter_component = CelsiusFromFahrenheitConverterComponent()

converter_tool = ComponentTool(
    component=converter_component,
    name="celsius_from_fahrenheit_converter",
    description="Convert Fahrenheit degrees to Celsius degrees."
)

web_tool = ComponentTool(
    component=web_search,
    name="web_search",
    description="Search the web for current information like weather, news, or facts.",
)

tool_calling_agent = Agent(
    chat_generator=GoogleGenAIChatGenerator(model=MODEL_ID),
    system_prompt="""You're a helpful agent. When asked about current information like weather, news, or facts,
                     use the web_search tool to find the information and then summarize the findings.
                     When you get web search results, extract the relevant information and present it in a clear,
                     concise manner. If you are asked to get the weather in Celsius degrees, use the `converter_tool` to convert
                     Fahrenheit degrees to Celsius and return both the temperature in Fahrenheit and Celsius.""",
    tools=[web_tool, converter_tool],
)

user_message = ChatMessage.from_user("What is the temperature in Bucharest in Celsius degrees?")
result = tool_calling_agent.run(messages=[user_message])

print(result["messages"][-1].text)