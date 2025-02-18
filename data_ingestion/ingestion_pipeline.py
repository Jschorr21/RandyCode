import sys
import os

# Add the root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_ingestion.vector_store import VectorStore
from data_ingestion.text_splitter import TextSplitter
from data_ingestion.json_loader import JSONLoader
from data_ingestion.csv_loader import CSVLoader
from data_ingestion.s3_loader import S3Loader
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
        # json_path = os.path.join(os.path.dirname(__file__), "data", "chunks.json")
        # json_loader = JSONLoader(json_path)
        # catalog_documents = json_loader.load_documents()

        # # Step 3: Load course data from CSV
        # csv_path = os.path.join(os.path.dirname(__file__), "data", "subject_courses.csv")
        # csv_loader = CSVLoader(csv_path)
        # course_documents = csv_loader.load_documents()

        # # Step 4: Store in vector database
        # self.vector_store.add_documents(catalog_documents, store_type="catalog")
        # self.vector_store.add_documents(course_documents, store_type="courses")

        # ✅ Load raw text files from S3
        bucket_name = "randy-scrape"
        s3_folder = "scraped_data/"

        print("📥 Loading text files from S3...")
        raw_documents = S3Loader(bucket_name, s3_folder).load_documents()

        if not raw_documents:
            print("❌ No `.txt` files found in S3.")
            return

        print("✅ Processing raw documents...")

        website_documents = []
        for doc in raw_documents:
            documents, metadatas, ids = self.text_splitter.chunk_text([doc])  # ✅ Fixed chunking

            print(f"✅ Created {len(documents)} text chunks from {doc.metadata['source']}.")

            self.text_splitter.save_chunks_to_json(documents, metadatas, ids, output_file=f"{doc.metadata['source']}.json")
            
            json_path = os.path.join(os.path.dirname(__file__), "data", f"{doc.metadata['source']}.json")
            json_loader = JSONLoader(json_path)
            public_documents = json_loader.load_documents()
            website_documents.extend(public_documents)

        print("✅ Text chunking and embedding ready.")

        self.vector_store.add_new_store("WebsiteData")
        self.vector_store.add_documents(website_documents, store_type="WebsiteData")


# Run pipeline
if __name__ == "__main__":
    ingestion = DataIngestionPipeline()
    ingestion.run()
