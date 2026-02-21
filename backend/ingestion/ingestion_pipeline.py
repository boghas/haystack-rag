import os

from utils.document_loader import fetch_documents_from_dataset
from haystack.components.writers import DocumentWriter
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack import Pipeline
from typing import List
from haystack import Document
from haystack.document_stores.in_memory import InMemoryDocumentStore

from dotenv import load_dotenv

load_dotenv(".env")


def run_ingestion_pipeline(
        documents: List[Document],
        document_store: InMemoryDocumentStore,
        embedding_model: str | None = os.getenv("EMBEDDING_MODEL")
    ):
    """"""

    if not embedding_model:
        raise ValueError(
            """"The embedding model is not set!
            You must provide an embedding model either by setting the "embedding_model" parameter
            or by setting the EMBEDDING_MODEL environment variable."""
        )
    
    document_embedder = SentenceTransformersDocumentEmbedder(model=embedding_model)
    document_embedder.warm_up()

    document_writer = DocumentWriter(document_store)

    indexing_pipeline = Pipeline()

    indexing_pipeline.add_component("document_embedder", document_embedder)
    indexing_pipeline.add_component("document_writer", document_writer)

    indexing_pipeline.connect("document_embedder", "document_writer")

    run_results = indexing_pipeline.run({"documents": documents})

    return run_results