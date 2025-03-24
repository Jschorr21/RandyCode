import sys
import os
import json

# Add the root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain.schema import Document
from data_ingestion.vector_store import VectorStore
from data_ingestion.json_loader import JSONLoader


class CatalogPipeline:
    def __init__(self):
        self.vector_store = VectorStore()
    
    def run(self, json_path, embed):
        # Step 1: Load catalog data from JSON
        json_loader = JSONLoader(json_path)
        catalog_documents = json_loader.load_documents()
        print(f"✅ Loaded {len(catalog_documents)} JSON chunks from {json_path}.")
        
        if embed:
            if not self.vector_store.stores.get("catalog"):
                self.vector_store.add_new_store("catalog")

            # Step 2: Store in vector database
            self.vector_store.add_documents(catalog_documents, store_type="catalog")
            print(f"✅ Embedded {len(catalog_documents)} documents into vector store.")


# Run pipeline with JSON file path passed as an argument
if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     print("Usage: python script.py <path_to_json> [--embed]")
    #     sys.exit(1)
    
    # json_file_path = sys.argv[1]
    embed_flag = "--embed" in sys.argv  # Check if embedding should happen
    
    ingestion = CatalogPipeline()
    ingestion.run("data/catalog.json", True)
