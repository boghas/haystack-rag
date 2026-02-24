import os
import logging
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever, InMemoryEmbeddingRetriever
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.utils import ComponentDevice
from haystack.components.joiners import DocumentJoiner
from haystack.components.rankers import TransformersSimilarityRanker
from haystack_integrations.components.rankers.amazon_bedrock import AmazonBedrockRanker 
from haystack.dataclasses import ChatMessage
from haystack.components.builders import ChatPromptBuilder
from haystack_integrations.components.generators.amazon_bedrock import AmazonBedrockChatGenerator
from haystack_integrations.components.embedders.amazon_bedrock import AmazonBedrockTextEmbedder
from haystack import Pipeline
from utils.files import read_txt_file

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
console_handler.setFormatter(formatter)

def run_hybrid_rag_pipeline(
        question: str,
        document_store: InMemoryDocumentStore,
        model_id: str | None = os.getenv("MODEL_ID")  
    ):
    """"""
    print(f"HYBRID_EMBEDDING_MODEL={os.getenv('EMBEDDING_MODEL')}")
    if not len(question.strip()) > 0:
        raise ValueError("The question is empty! Please provide a valid question.")
    
    if not model_id:
        raise ValueError(
            """LLM model is empty!
            Please provide an LLM model as a parameter or set the MODEL_ID environment variable!"""
            )
    
    if not os.getenv("HYBRID_EMBEDDING_MODEL"):
        raise ValueError(
            """Embedding model is empty!
            Please provide an embedding model as a parameter or set the HYBRID_EMBEDDING_MODEL environment variable!"""
            )
    
    prompt = read_txt_file(os.getenv("RAG_TEMPLATE_PATH"))

    prompt_template = [ChatMessage.from_user(prompt)]
    prompt_builder = ChatPromptBuilder(template=prompt_template)

    generator = AmazonBedrockChatGenerator(model=model_id)
    
    embedder = AmazonBedrockTextEmbedder(model=os.getenv("EMBEDDING_MODEL"))

    bm25_retriever = InMemoryBM25Retriever(document_store=document_store)
    embeddings_retriever = InMemoryEmbeddingRetriever(document_store=document_store)

    document_joiner = DocumentJoiner()

    # similarity_ranker = TransformersSimilarityRanker(model="BAAI/bge-reranker-base")
    similarity_ranker = AmazonBedrockRanker(model="amazon.rerank-v1:0")

    hybrid_rag_pipeline = Pipeline()

    hybrid_rag_pipeline.add_component("text_embedder", embedder)
    hybrid_rag_pipeline.add_component("embeddings_retriever", embeddings_retriever)
    hybrid_rag_pipeline.add_component("bm25_retriever", bm25_retriever)
    hybrid_rag_pipeline.add_component("joiner", document_joiner)
    hybrid_rag_pipeline.add_component("ranker", similarity_ranker)
    hybrid_rag_pipeline.add_component("prompt_builder", prompt_builder)
    hybrid_rag_pipeline.add_component("llm", generator)

    hybrid_rag_pipeline.connect("text_embedder.embedding", "embeddings_retriever.query_embedding")
    hybrid_rag_pipeline.connect("bm25_retriever", "joiner")
    hybrid_rag_pipeline.connect("embeddings_retriever", "joiner")
    hybrid_rag_pipeline.connect("joiner", "ranker")
    hybrid_rag_pipeline.connect("ranker", "prompt_builder")
    hybrid_rag_pipeline.connect("prompt_builder.prompt", "llm.messages")

    response = hybrid_rag_pipeline.run(
        {
            "text_embedder": {
                "text": question,
            },
            "bm25_retriever": {
                "query": question,
            },
            "ranker": {
                "query": question,
                "top_k": 10
            },
            "prompt_builder": {
                "question": question,
            },
        },
    )

    return response["llm"]["replies"][0].text
    
