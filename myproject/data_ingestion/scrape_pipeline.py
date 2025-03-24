import sys
import os
import json
import re
import traceback
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
        self.json_root = os.path.join(os.path.dirname(__file__), "data", "scraped_data")  # JSON storage directory

    def clean_json_file(self, json_path):
        """Removes chunks that contain only '=' characters from the JSON file."""
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                chunks = json.load(f)

            # Filter out chunks where the "text" field contains only '=' (any number of them)
            cleaned_chunks = [chunk for chunk in chunks if not re.fullmatch(r"=+", chunk.get("text", "").strip())]

            if len(cleaned_chunks) != len(chunks):
                print(f"🧹 Cleaned {len(chunks) - len(cleaned_chunks)} chunks from {json_path}")

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
            documents, metadatas, ids = self.text_splitter.chunk_scraped_text([doc])  # ✅ Fixed chunking

            print(f"✅ Created {len(documents)} text chunks from {doc.metadata['source']}.")

            json_output_path = os.path.join(self.json_root, f"{doc.metadata['source']}.json")

            # ✅ Ensure `scraped_data/` does not appear twice
            if "scraped_data/scraped_data" in json_output_path:
                json_output_path = json_output_path.replace("scraped_data/scraped_data", "scraped_data")


            self.text_splitter.save_chunks_to_json(documents, metadatas, ids, output_file=json_output_path)

        # ✅ Clean the extracted JSON data
        print("🧹 Cleaning JSON files before ingestion...")
        self.clean_all_json_files()
        seen_files = set()
        # ✅ Load cleaned JSON files into memory for vector storage
        for subdir, _, files in os.walk(self.json_root, followlinks=False):
            
            for file in files:
                if file.endswith(".json"):
                    # print(f"📝 Before extending: {len(website_documents)}")
                    json_path = os.path.join(subdir, file)
                    print(f"🔍 Visiting file: {json_path}")

                    if json_path in seen_files:
                        print("skipping dupe visit")
                        continue
                    seen_files.add(json_path)
                    json_loader = JSONLoader(json_path)
                    public_documents = json_loader.load_documents()
                    website_documents.extend(public_documents)
                    # print(f"📝 After extending: {len(website_documents)} (Added {len(public_documents)})")


        print("✅ Text chunking and embedding ready.")

        # ✅ Ensure the vector store exists
        if not self.vector_store.stores.get("websites"):
            self.vector_store.add_new_store("websites")

        # ✅ Retrieve existing document IDs before inserting new ones
        existing_docs = self.vector_store.stores["websites"].get(include=["metadatas"]).get("metadatas", [])
        existing_ids = {meta["id"] for meta in existing_docs if "id" in meta}

        # ✅ Deduplicate chunks before insertion
        unique_documents = []
        seen_chunk_ids = set()

        for doc in website_documents:
            doc_id = doc.metadata["id"]

            # Avoid inserting duplicates by checking both stored and already-seen IDs
            if doc_id not in existing_ids and doc_id not in seen_chunk_ids:
                unique_documents.append(doc)
                seen_chunk_ids.add(doc_id)
            # else:
                # print(f"🚫 Skipping duplicate chunk {doc_id}")

        # 🚀 Ensure add_documents() is called only once
        print(f"✅ Attempting to insert {len(unique_documents)} new chunks (Skipping {len(website_documents) - len(unique_documents)} duplicates)")

        if unique_documents:
            self.vector_store.add_documents(unique_documents, store_type="websites")
        else:
            print("🚫 No new chunks to insert.")



# Run pipeline
if __name__ == "__main__":
    ingestion = ScrapePipeline()
    ingestion.run()
