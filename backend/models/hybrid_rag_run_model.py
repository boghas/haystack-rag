from pydantic import BaseModel

class TextEmbedderModel(BaseModel):
    text: str

class BM25RetrieverModel(BaseModel):
    query: str

class RankerModel(BaseModel):
    query: str
    top_k: int

class PromptBuilderModel(BaseModel):
    question: str

class HybridRagRunModel(BaseModel):
    text_embedder: TextEmbedderModel
    bm25_retriever: BM25RetrieverModel
    ranker: RankerModel
    prompt_builder: PromptBuilderModel
