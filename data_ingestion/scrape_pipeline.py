import sys
import os

# Add the root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_ingestion.vector_store import VectorStore
from data_ingestion.text_splitter import TextSplitter
from data_ingestion.json_loader import JSONLoader
from data_ingestion.csv_loader import CSVLoader
from data_ingestion.s3_loader import S3Loader

class ScrapePipeline:
    def __init__(self):
        self.vector_store = VectorStore()
        self.text_splitter = TextSplitter()
    

    def run(self):
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
            documents, metadatas, ids = self.text_splitter.chunk_scraped_text([doc])  # ✅ Fixed chunking

            print(f"✅ Created {len(documents)} text chunks from {doc.metadata['source']}.")

            self.text_splitter.save_chunks_to_json(documents, metadatas, ids, output_file=f"{doc.metadata['source']}.json")
            
            json_path = os.path.join(os.path.dirname(__file__), "data", f"{doc.metadata['source']}.json")
            json_loader = JSONLoader(json_path)
            public_documents = json_loader.load_documents()
            website_documents.extend(public_documents)

        print("✅ Text chunking and embedding ready.")

        if not self.vector_store.stores["websites"]:
            self.vector_store.add_new_store("websites")

        self.vector_store.add_documents(website_documents, store_type="websites")


# Run pipeline
if __name__ == "__main__":
    ingestion = ScrapePipeline()
    ingestion.run()
