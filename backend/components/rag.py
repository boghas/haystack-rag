from haystack import component
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore
from rag import hybrid_rag_pipeline

@component
class HybridRAGComponent:

    def __init__(self, document_store: InMemoryDocumentStore | OpenSearchDocumentStore):
        self.document_store = document_store
    
    @component.output_types(response=str)
    def run(self, message: str):
        response = hybrid_rag_pipeline.run_hybrid_rag_pipeline(question=message, document_store=self.document_store)

        return {"response": response}