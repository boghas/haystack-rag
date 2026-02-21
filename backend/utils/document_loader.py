from datasets import load_dataset
from haystack import Document
from typing import List


def fetch_documents_from_dataset(dataset_name: str, split: str = "train") -> List[Document]:
    """Fetch documents from a dataset.
    
    Args:
        dataset_name (str): The dataset to load documents from.
        split (str): The split to be used. Defaults to "train".
    
    Returns:
        A List of Haystack Document obtained from the dataset.
    """

    dataset = load_dataset(path=dataset_name, split=split)
    docs = [Document(content=doc["content"], meta=doc["meta"]) for doc in dataset]

    return docs