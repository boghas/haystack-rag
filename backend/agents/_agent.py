import os
import json
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack_integrations.components.generators.amazon_bedrock import AmazonBedrockChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.tools.tool import Tool
from haystack.components.agents import Agent
from haystack.utils import Secret
from haystack_integrations.components.generators.google_genai import GoogleGenAIChatGenerator
from typing import List, Dict

from dotenv import load_dotenv

load_dotenv(".env")

# MODEL_ID = os.getenv("MODEL_ID", "")
MODEL_ID = "gemini-2.5-flash"

## Tool Function
def calculate(expression: str) -> dict:
    try:
        result = eval(expression, {"__builtins__": {}})
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

def read_txt_file_by_name(file_name: str) -> Dict[str, str]:
    """Read the contents of a file and return the contents.
    
    Args:
        file_name (str): The file name to read the contents from. Example: "test.txt".
    
    Returns:
        Dict[str, str]: A dictionary with the contents of the file. Example: {"contents": "..."}
    """
    print(f"file_request: {file_name}")
    contents: str = ""
    data: list[str] = []
    file_path: str = os.path.join("agents", file_name)
    try:
        with open(file_path, "r", encoding="utf-8") as fl:
            data: list[str] = fl.readlines()
    except FileNotFoundError:
        raise
    except Exception as ex:
        print(f"Caught exception ex: {ex}")
        raise
    finally:
        contents = "\n".join(data)
    
    print(f"contents: {contents}")
    
    return {"contents": contents}

## Tool Definition
calculator_tool = Tool(
    name="calculator",
    description="Evaluate basic math expressions.",
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Math expression to evaluate",
            },
        },
        "required": ["expression"],
    },
    function=calculate,
    outputs_to_state={"calc_result": {"source": "result"}},
)

read_file_tool = Tool(
    name="file_reader",
    description="Read txt files by name and return the contents of the file.",
    parameters={
        "type": "object",
        "properties": {
            "file_name": {
                "type": "string",
                "description": "The file name to read contents from.",
            }
        },
        "required": ["file_name"],
    },
    function=read_txt_file_by_name,
    outputs_to_state={"file_contents": {"source": "contents"}}
)

## Agent Setup
agent = Agent(
    chat_generator=GoogleGenAIChatGenerator(model=MODEL_ID),
    tools=[calculator_tool, read_file_tool],
    exit_conditions=["text"],
    state_schema={"file_contents": {"type": str}},
)

## Run the Agent
# response = agent.run(messages=[ChatMessage.from_user("What is 7 * (4 + 2)?")])
response = agent.run(messages=[ChatMessage.from_user("What does the test.txt file say?")])

print("Response:", response["messages"][-1].text)