import pymupdf4llm
from haystack import component
from haystack.dataclasses import Document
from typing import List
from pathlib import Path


@component
class PdfToMarkdownDocumentProcessor:

    def __init__(self, file_paths: List[Path] | None):
        self.file_paths = file_paths
    
    def _convert_llama_docs(self):
        haystack_documents: List[Document] = []

        for llama_doc in self.llama_docs:
            haystack_documents.append(Document(
                    id=llama_doc.doc_id,
                    content=llama_doc.get_content(),
                    meta=llama_doc.metadata
                )
            )
        
        return haystack_documents

    @component.output_types(documents=List[Document])
    def run(self):
        self.documents: List[Document] = []
        self.llama_reader = pymupdf4llm.LlamaMarkdownReader()

        for pdf_file in self.file_paths:
            self.llama_docs = self.llama_reader.load_data(pdf_file)
            self.documents.extend(self._convert_llama_docs())
        
        return {"documents": self.documents}

