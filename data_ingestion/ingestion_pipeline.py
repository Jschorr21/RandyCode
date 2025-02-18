import sys
import os

# Add the root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_ingestion.vector_store import VectorStore
from data_ingestion.text_splitter import TextSplitter
from data_ingestion.json_loader import JSONLoader
from data_ingestion.csv_loader import CSVLoader

class DataIngestionPipeline:
    """Handles the complete data ingestion process."""

    def __init__(self):
        self.vector_store = VectorStore()
        self.text_splitter = TextSplitter()

    def run(self):
        """Runs the full ingestion pipeline."""

        # Step 1: Extract & chunk PDF text
        # pdf_path = os.path.join(os.path.dirname(__file__), "data", "Undergraduate_Catalog_2024-25.pdf")
        # text_list = self.text_splitter.extract_text_from_pdf(pdf_path)
        # documents, metadatas, ids = self.text_splitter.chunk_text(text_list)

        # # Save extracted chunks to JSON
        # self.text_splitter.save_chunks_to_json(documents, metadatas, ids)

        # Step 2: Load catalog data from JSON
        json_path = os.path.join(os.path.dirname(__file__), "data", "chunks.json")
        json_loader = JSONLoader(json_path)
        catalog_documents = json_loader.load_documents()

        # Step 3: Load course data from CSV
        csv_path = os.path.join(os.path.dirname(__file__), "data", "subject_courses.csv")
        csv_loader = CSVLoader(csv_path)
        course_documents = csv_loader.load_documents()

        # Step 4: Store in vector database
        self.vector_store.add_documents(catalog_documents, store_type="catalog")
        self.vector_store.add_documents(course_documents, store_type="courses")

# Run pipeline
if __name__ == "__main__":
    ingestion = DataIngestionPipeline()
    ingestion.run()
