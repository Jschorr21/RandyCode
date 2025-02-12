import json
from langchain_core.documents import Document

def load_json_documents(file_path):
    """Loads JSON documents and converts them to LangChain Document objects."""
    with open(file_path, "r", encoding="utf-8") as file:
        chunk_data = json.load(file)

    return [
        Document(
            page_content=chunk["text"],
            metadata={"id": chunk["id"], "page": chunk["metadata"]["page"], "source": "chunks.json"}
        )
        for chunk in chunk_data
    ]
