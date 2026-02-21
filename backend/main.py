from fastapi import FastAPI, BackgroundTasks
from ingestion.ingestion_pipeline import run_ingestion_pipeline
from rag.rag_pipeline import run_rag_pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from utils.document_loader import fetch_documents_from_dataset

app = FastAPI()

document_store = InMemoryDocumentStore()


@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/ingest-data")
async def ingest_data(background_tasks: BackgroundTasks):
    documents = fetch_documents_from_dataset(dataset_name="bilgeyucel/seven-wonders")
    background_tasks.add_task(run_ingestion_pipeline, documents, document_store)

    return {"message": "Ingestion process is started..."}

@app.get("/chat")
async def chat(question: str):
    response = run_rag_pipeline(question, document_store)

    return {"response": response}

