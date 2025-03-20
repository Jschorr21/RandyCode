import json
import os
from langchain.schema import Document

class JSONLoader:
    """Loads course chunks from JSON and converts them into LangChain Documents."""

    def __init__(self, file_path):
        """Ensures the file path does not contain duplicate `scraped_data/` references."""
        base_dir = os.path.dirname(__file__)

        # ✅ Remove duplicate `scraped_data/` from path
        while "scraped_data/scraped_data" in file_path:
            file_path = file_path.replace("scraped_data/scraped_data", "scraped_data")

        # ✅ Convert to absolute path
        if not os.path.isabs(file_path):
            file_path = os.path.join(base_dir, file_path)

        self.file_path = os.path.abspath(file_path)


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
        print(f"📂 Loaded {len(documents)} chunks from {self.file_path}")
        return documents

# Usage:
if __name__ == "__main__":
    json_loader = JSONLoader("chunks.json")
    documents = json_loader.load_documents()
    print(f"✅ Loaded {len(documents)} JSON chunks.")
