import os
from pathlib import Path
from typing import List
from utils.config import EMBEDDING_MODEL
from haystack.components.converters.pypdf import PyPDFToDocument
from haystack.components.preprocessors.document_splitter import DocumentSplitter
from haystack_integrations.components.embedders.amazon_bedrock import AmazonBedrockDocumentEmbedder
from haystack.components.embedders.sentence_transformers_document_embedder import SentenceTransformersDocumentEmbedder
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.writers.document_writer import DocumentWriter
from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore
from haystack import Pipeline
from models.responses.ingestion import IngestionResponseModel
from models.statuses.process_status import ProcessStatus


def run_file_ingestion_pipeline(
        file_paths: List[Path],
        document_store: InMemoryDocumentStore | OpenSearchDocumentStore,
        embedding_model: str = EMBEDDING_MODEL,
    ) -> IngestionResponseModel:
    """"""
    response = IngestionResponseModel(
        files=file_paths,
        status=ProcessStatus.RUNNING,
        nr_of_files=len(file_paths)
    )

    converter = PyPDFToDocument()
    splitter = DocumentSplitter(split_by="sentence", split_length=5)
    embedder = SentenceTransformersDocumentEmbedder(model=embedding_model)
    embedder.warm_up()

    writer = DocumentWriter(document_store=document_store)

    pipeline = Pipeline()

    pipeline.add_component("converter", converter)
    pipeline.add_component("splitter", splitter)
    pipeline.add_component("embedder", embedder)
    pipeline.add_component("writer", writer)

    pipeline.connect("converter.documents", "splitter.documents")
    pipeline.connect("splitter.documents", "embedder.documents")
    pipeline.connect("embedder.documents", "writer.documents")

    try:
        result = pipeline.run({"sources": file_paths})

        response.status = ProcessStatus.COMPLETED
        response.documents_written = result["writer"]["documents_written"]

        return response
    except Exception as ex:
        print(f"Failed running hybrid pipeline... {ex}")
        response.status = ProcessStatus.FAILED
        response.error_message = str(ex)
    
    return response
