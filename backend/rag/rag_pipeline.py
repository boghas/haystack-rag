import os

from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.generators.amazon_bedrock import AmazonBedrockChatGenerator
from haystack.components.builders import ChatPromptBuilder
from haystack.dataclasses import ChatMessage
from haystack import Pipeline
from utils.files import read_txt_file

from dotenv import load_dotenv

load_dotenv(".env")

RAG_TEMPLATE_PATH = "templates/rag_template.jinja2"

def run_rag_pipeline(
        question: str,
        document_store: InMemoryDocumentStore,
        embedding_model: str | None = os.getenv("EMBEDDING_MODEL"),
    ) -> str:
    """"""
    if not embedding_model:
        raise ValueError(
            """"The embedding model is not set!
            You must provide an embedding model either by setting the "embedding_model" parameter
            or by setting the EMBEDDING_MODEL environment variable."""
        )
    
    if not len(question.strip()) > 0:
        raise ValueError("The question is empty! Please provide a valid question.")
    
    text_embedder = SentenceTransformersTextEmbedder(embedding_model)

    retriever = InMemoryEmbeddingRetriever(document_store)

    prompt = read_txt_file(RAG_TEMPLATE_PATH)

    prompt_template = [ChatMessage.from_user(prompt)]
    prompt_builder = ChatPromptBuilder(prompt_template)

    chat_generator = AmazonBedrockChatGenerator(model=os.getenv("MODEL_ID"))

    rag_pipeline = Pipeline()

    rag_pipeline.add_component("text_embedder", text_embedder)
    rag_pipeline.add_component("retriever", retriever)
    rag_pipeline.add_component("prompt_builder", prompt_builder)
    rag_pipeline.add_component("llm", chat_generator)

    rag_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
    rag_pipeline.connect("retriever", "prompt_builder")
    rag_pipeline.connect("prompt_builder.prompt", "llm.messages")

    response = rag_pipeline.run({"text_embedder": {"text": question}, "prompt_builder": {"question": question}})

    return response["llm"]["replies"][0].text


