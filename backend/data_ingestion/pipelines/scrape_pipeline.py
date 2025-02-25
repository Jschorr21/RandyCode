import sys
import os
import json
import re

# Add the root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_ingestion.vector_store import VectorStore
from data_ingestion.text_splitter import TextSplitter
from data_ingestion.json_loader import JSONLoader
from data_ingestion.s3_loader import S3Loader


class ScrapePipeline:
    def __init__(self):
        self.vector_store = VectorStore()
        self.text_splitter = TextSplitter()
        self.json_root = os.path.join(
            os.path.dirname(__file__), "data", "scraped_data"
        )  # JSON storage directory

    def clean_json_file(self, json_path):
        """Removes chunks that contain only '=' characters from the JSON file."""
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                chunks = json.load(f)

            # Filter out chunks where the "text" field contains only '=' (any number of them)
            cleaned_chunks = [
                chunk
                for chunk in chunks
                if not re.fullmatch(r"=+", chunk.get("text", "").strip())
            ]

            if len(cleaned_chunks) != len(chunks):
                print(
                    f"🧹 Cleaned {len(chunks) - len(cleaned_chunks)} chunks from {json_path}"
                )

                # Save the cleaned data back to the same JSON file
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(cleaned_chunks, f, indent=2, ensure_ascii=False)

        except json.JSONDecodeError:
            print(f"⚠️ Skipping {json_path}: Invalid JSON format.")

    def clean_all_json_files(self):
        """Loops through all subfolders in the JSON storage directory and cleans each JSON file."""
        for subdir, _, files in os.walk(self.json_root):
            for file in files:
                if file.endswith(".json"):
                    json_path = os.path.join(subdir, file)
                    self.clean_json_file(json_path)

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
            documents, metadatas, ids = self.text_splitter.chunk_scraped_text(
                [doc]
            )  # ✅ Fixed chunking

            print(
                f"✅ Created {len(documents)} text chunks from {doc.metadata['source']}."
            )

            json_output_path = os.path.join(
                self.json_root, f"{doc.metadata['source']}.json"
            )
            self.text_splitter.save_chunks_to_json(
                documents, metadatas, ids, output_file=json_output_path
            )

        # ✅ Clean the extracted JSON data
        print("🧹 Cleaning JSON files before ingestion...")
        self.clean_all_json_files()

        # ✅ Load cleaned JSON files into memory for vector storage
        for subdir, _, files in os.walk(self.json_root):
            for file in files:
                if file.endswith(".json"):
                    json_path = os.path.join(subdir, file)
                    json_loader = JSONLoader(json_path)
                    public_documents = json_loader.load_documents()
                    website_documents.extend(public_documents)

        print("✅ Text chunking and embedding ready.")

        if not self.vector_store.stores.get("websites"):
            self.vector_store.add_new_store("websites")

        self.vector_store.add_documents(website_documents, store_type="websites")


# Run pipeline
if __name__ == "__main__":
    ingestion = ScrapePipeline()
    ingestion.run()
