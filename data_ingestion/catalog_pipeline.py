import sys
import os
import json
import os

# Add the root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain.schema import Document
from data_ingestion.vector_store import VectorStore
from data_ingestion.text_splitter import TextSplitter
from data_ingestion.json_loader import JSONLoader
from data_ingestion.csv_loader import CSVLoader
from data_ingestion.s3_loader import S3Loader


class CatalogPipeline:
    def __init__(self):
        self.vector_store = VectorStore()
        self.text_splitter = TextSplitter()

    # def load_documents(self, file_path):
    #     """Reads JSON and converts it into a list of Document objects."""

    #     # ✅ Extract filename without extension
    #     file_path = os.path.join(os.path.dirname(__file__), file_path)

    #     with open(file_path, "r", encoding="utf-8") as file:
    #         chunk_data = json.load(file)

    #     documents = [
    #         Document(
    #             page_content=chunk["text"],
    #             metadata={"id": chunk["id"], "page": chunk["metadata"]["page"], "source": "Catalog"}
    #         )
    #         for chunk in chunk_data
    #     ]

    #     return documents

    def run(self, embed):
        
        # Step 1: Extract & chunk PDF text
        pdf_path = os.path.join(os.path.dirname(__file__), "data", "Undergraduate_Catalog_2024-25.pdf")
        print(f"📥 Extracting text from PDF: {pdf_path}")
        text_list = self.text_splitter.extract_text_from_pdf(pdf_path)
        print(f"✅ Extracted {len(text_list)} pages of text.")

        documents, metadatas, ids = self.text_splitter.chunk_pdf_text(text_list)
        print(f"✅ Chunked {len(documents)} text chunks.")

        # Save extracted chunks to JSON
        self.text_splitter.save_chunks_to_json(documents, metadatas, ids, "catalog.json")

        # Step 2: Load catalog data from JSON
        json_path = os.path.join(os.path.dirname(__file__), "data", "catalog.json")
        json_loader = JSONLoader(json_path)
        catalog_documents = json_loader.load_documents()
        print(f"✅ Loaded {len(catalog_documents)} JSON chunks.")
        if embed:
            if not self.vector_store.stores["catalog"]:
                self.vector_store.add_new_store("catalog")

            # Step 3: Store in vector database
            self.vector_store.add_documents(catalog_documents, store_type="catalog")

# Run pipeline
if __name__ == "__main__":
    ingestion = CatalogPipeline()
    ingestion.run(embed = False)