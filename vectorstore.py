from langchain_chroma import Chroma  # New import based on the warning

from embeddings import embeddings

PERSIST_DIRECTORY = "./chroma_db"

# Initialize Chroma stores
catalog_store = Chroma(collection_name="Catalog", embedding_function=embeddings, persist_directory=PERSIST_DIRECTORY)
courses_store = Chroma(collection_name="Courses", embedding_function=embeddings, persist_directory=PERSIST_DIRECTORY)

def get_documents_from_store(store):
    return store.get()

print(f"ChromaDB is stored at: {PERSIST_DIRECTORY}")
