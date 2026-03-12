import os
import tempfile
from fastapi import FastAPI, BackgroundTasks, UploadFile, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ingestion.file_ingestion_pipeline import run_file_ingestion_pipeline
from rag.rag_pipeline import run_rag_pipeline
from rag.hybrid_rag_pipeline import run_hybrid_rag_pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from utils.document_loader import fetch_documents_from_dataset
from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore
from typing import Annotated, List
from utils.config import TEMP_DIR
from utils.files import save_uploaded_files
from utils.auth import get_current_active_user, fake_hashed_password
from fake_db.fake_db import fake_users
from models.user import User, UserInDB


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

document_store = InMemoryDocumentStore()
# document_store = OpenSearchDocumentStore(
#     hosts=["http://ec2-34-244-79-36.eu-west-1.compute.amazonaws.com:9200", "http://ec2-34-244-79-36.eu-west-1.compute.amazonaws.com:9201"],
#     index="test-index",
#     embedding_dim=384,
# )

if document_store:
    print(f"Document store loaded successfully")


@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users.get(form_data.username)
    if not user_dict:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password"
        )
    
    user = UserInDB(**user_dict)
    hashed_password = fake_hashed_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    return {"access_token": user.username, "token_type": "bearer"}

@app.get("/api/v1/users/me")
async def get_current_user(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user

@app.get("/api/v1/doc_count")
async def read_doc_count(token: Annotated[str, Depends(oauth2_scheme)]):
    doc_count: int = document_store.count_documents()

    return {"doc_count": doc_count}


# @app.get("/doc_count")
# async def read_doc_count():
#     doc_count: int = document_store.count_documents()

#     return {"doc_count": doc_count}

@app.get("/api/v1/documents")
async def get_all_documents():
    documents = document_store.filter_documents()

    return {"documents": documents}


@app.post("/api/v1/ingest-files")
async def ingest_files(files: List[UploadFile], background_tasks: BackgroundTasks):
    file_paths = await save_uploaded_files(files=files, local_dir=TEMP_DIR)
    background_tasks.add_task(run_file_ingestion_pipeline, file_paths,  document_store)

    return {"nr_of_files": len(file_paths), "message": "Launhed ingestion process.."}

@app.get("/chat")
async def chat(question: str):
    response = run_rag_pipeline(question, document_store)

    return {"response": response}

@app.get("/api/v1/chat")
async def hybrid_chat(question: str):
    response = run_hybrid_rag_pipeline(question=question, document_store=document_store)

    return {"response": response}

