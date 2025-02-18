import json
import os
from langchain.schema import Document

class JSONLoader:
    """Loads course chunks from JSON and converts them into LangChain Documents."""

    def __init__(self, file_path):
        self.file_path = os.path.join(os.path.dirname(__file__), file_path)

    def load_documents(self, source="chunks.json"):
        """Reads JSON and converts it into a list of Document objects."""
        with open(self.file_path, "r", encoding="utf-8") as file:
            chunk_data = json.load(file)

        documents = [
            Document(
                page_content=chunk["text"],
                metadata={"id": chunk["id"], "page": chunk["metadata"]["page"], "source": source}
            )
            for chunk in chunk_data
        ]

        return documents

# Usage:
if __name__ == "__main__":
    json_loader = JSONLoader("chunks.json")
    documents = json_loader.load_documents()
    print(f"✅ Loaded {len(documents)} JSON chunks.")
