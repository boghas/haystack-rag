from haystack.components.websearch import SerperDevWebSearch
from haystack import Document
from haystack import component
from typing import List

from dotenv import load_dotenv

load_dotenv("")

@component
class WebSearchComponent:

    @component.output_types(documents=List[Document])
    def run(
        self,
        query: str
    ):
        """"""
        if not len(query.strip()) > 0:
            raise ValueError("Query cannot be empty! Please provide a value query.")
        
        search = SerperDevWebSearch(top_k=3)

        return search.run(query=query)
