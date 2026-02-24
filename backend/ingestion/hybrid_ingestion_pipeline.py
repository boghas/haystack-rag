import os
from haystack.components.writers import DocumentWriter
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack_integrations.components.embedders.amazon_bedrock import AmazonBedrockDocumentEmbedder
from haystack.components.preprocessors.document_splitter import DocumentSplitter
from haystack import Pipeline
from haystack.utils import ComponentDevice
from typing import List
from haystack import Document
from haystack.document_stores.in_memory import InMemoryDocumentStore


def run_hybrid_ingestion_pipeline(
        documents: List[Document],
        document_store: InMemoryDocumentStore,
        embedding_model: str | None = os.getenv("EMBEDDING_MODEL")
    ):
    """"""
    print(f"HYBRID_EMBEDDING_MODEL={os.getenv("EMBEDDING_MODEL")}")
    if not embedding_model:
        raise ValueError(
            """Embedding model is empty!
            Please provide an embedding model as a parameter or set the HYBRID_EMBEDDING_MODEL as environment variable!"""
            )
    
    document_splitter = DocumentSplitter(split_by="word", split_length=512, split_overlap=32)
    document_embedder = AmazonBedrockDocumentEmbedder(
        model=embedding_model, device=ComponentDevice.from_str("cuda:0")
    )
    document_writter = DocumentWriter(document_store=document_store)

    hybrid_indexing_pipeline = Pipeline()

    hybrid_indexing_pipeline.add_component("document_splitter", document_splitter)
    hybrid_indexing_pipeline.add_component("document_embedder", document_embedder)
    hybrid_indexing_pipeline.add_component("document_writter", document_writter)

    hybrid_indexing_pipeline.connect("document_splitter", "document_embedder")
    hybrid_indexing_pipeline.connect("document_embedder", "document_writter")

    run_results = hybrid_indexing_pipeline.run({"document_splitter": {"documents": documents}})

    return run_results