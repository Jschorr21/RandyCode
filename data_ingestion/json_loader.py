import json
import os
from langchain.schema import Document

class JSONLoader:
    """Loads course chunks from JSON and converts them into LangChain Documents."""

    def __init__(self, file_path):
        self.file_path = os.path.join(os.path.dirname(__file__), file_path)

    def load_documents(self):
        """Reads JSON and converts it into a list of Document objects."""
        
        # ✅ Extract filename without extension
        source_filename = os.path.basename(self.file_path).replace(".json", "")

        with open(self.file_path, "r", encoding="utf-8") as file:
            chunk_data = json.load(file)

        documents = [
            Document(
                page_content=chunk["text"],
                metadata={
                    "id": chunk["id"],
                    "chunk_number": chunk["metadata"]["chunk_number"],
                    "source": source_filename  # ✅ Use the filename dynamically
                }
            )
            for chunk in chunk_data
        ]

        return documents

# Usage:
if __name__ == "__main__":
    json_loader = JSONLoader("chunks.json")
    documents = json_loader.load_documents()
    print(f"✅ Loaded {len(documents)} JSON chunks.")
