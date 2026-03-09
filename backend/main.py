import os
import tempfile
from fastapi import FastAPI, BackgroundTasks, UploadFile
from ingestion.ingestion_pipeline import run_ingestion_pipeline
from ingestion.hybrid_ingestion_pipeline import run_hybrid_ingestion_pipeline
from ingestion.file_ingestion_pipeline import run_file_ingestion_pipeline
from rag.rag_pipeline import run_rag_pipeline
from rag.hybrid_rag_pipeline import run_hybrid_rag_pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from utils.document_loader import fetch_documents_from_dataset
from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore
from typing import List
from utils.config import TEMP_DIR
from utils.files import save_uploaded_files

app = FastAPI()

document_store = InMemoryDocumentStore()
# document_store = OpenSearchDocumentStore(
#     hosts=["http://ec2-34-244-79-36.eu-west-1.compute.amazonaws.com:9200", "http://ec2-34-244-79-36.eu-west-1.compute.amazonaws.com:9201"],
#     index="test-index",
#     embedding_dim=384,
# )

# document_store.create_index("test-index")
# print(f"indexed created successfully")

if document_store:
    print(f"Document store loaded successfully")


@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/doc_count")
async def read_doc_count():
    doc_count: int = document_store.count_documents()

    return {"doc_count": doc_count}

@app.get("/api/v1/documents")
async def get_all_documents():
    documents = document_store.filter_documents()

    return {"documents": documents}


@app.post("/api/v1/ingest-files/")
async def ingest_files(files: List[UploadFile], background_tasks: BackgroundTasks):
    file_paths = await save_uploaded_files(files=files, local_dir=TEMP_DIR)
    background_tasks.add_task(run_file_ingestion_pipeline, file_paths,  document_store)

    return {"nr_of_files": len(file_paths), "message": "Launhed ingestion process.."}


@app.post("/ingest-data")
async def ingest_data(background_tasks: BackgroundTasks):
    documents = fetch_documents_from_dataset(dataset_name="bilgeyucel/seven-wonders")
    background_tasks.add_task(run_ingestion_pipeline, documents, document_store)

    return {"message": "Ingestion process is started..."}

@app.post("/hybrid-ingestion")
async def hybrid_ingest_data(backgrounds_tasks: BackgroundTasks):
    documents = fetch_documents_from_dataset(dataset_name="bilgeyucel/seven-wonders")
    backgrounds_tasks.add_task(run_hybrid_ingestion_pipeline, documents, document_store)

    return {"message": "Hybrid ingestion process is started..."}

@app.get("/chat")
async def chat(question: str):
    response = run_rag_pipeline(question, document_store)

    return {"response": response}

@app.get("/hybrid-chat")
async def hybrid_chat(question: str):
    response = run_hybrid_rag_pipeline(question=question, document_store=document_store)

    return {"response": response}

