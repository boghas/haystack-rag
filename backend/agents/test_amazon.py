import os
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.amazon_bedrock import AmazonBedrockChatGenerator

from dotenv import load_dotenv

load_dotenv(".env")

MODEL_ID = os.getenv("MODEL_ID", "")
print(f"using: {MODEL_ID} model")

generator = AmazonBedrockChatGenerator(model=MODEL_ID)
message = ChatMessage.from_user(text="Give me a greeting message")

result = generator.run(messages=[message])

print(result)