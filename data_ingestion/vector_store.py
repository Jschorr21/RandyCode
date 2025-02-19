import os
from dotenv import load_dotenv
import getpass
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import hashlib

class VectorStore:
    """Handles ChromaDB vector storage for multiple collections."""

    def __init__(self, persist_directory="./chroma_db"):
        """
        Initializes Chroma vector database.
        
        Args:
            persist_directory (str): Path to persist ChromaDB collections.
        """
        print("Initializing Vector Store...")
        self._set_env_variables()
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.persist_directory = persist_directory

        # Dictionary to store multiple Chroma collections
        self.stores = {
            "catalog": self._init_store("Catalog"),
            "courses": self._init_store("Courses"),
            "websites": self._init_store("WebsiteData")
        }

        print(f"✅ ChromaDB initialized at: {self.persist_directory}")

    def _set_env_variables(self):
        """Sets API keys from .env file, falling back to manual input if not found."""
        # Load environment variables from .env file
        load_dotenv()

        # Dictionary of required API keys
        required_keys = {
            "LANGSMITH_API_KEY": "Langsmith",
            "LANGCHAIN_API_KEY": "Langchain",
            "OPENAI_API_KEY": "OpenAI"
        }

        # Check each required key
        for env_var, service_name in required_keys.items():
            if not os.getenv(env_var):
                os.environ[env_var] = getpass.getpass(f"Enter API key for {service_name}: ")

    def _init_store(self, collection_name):
        """Initializes a Chroma collection."""
        return Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

    def add_new_store(self, store_name):
        """
        Adds a new vector store dynamically.

        Args:
            store_name (str): The name of the new collection.
        """
        if store_name not in self.stores:
            self.stores[store_name] = self._init_store(store_name)
            print(f"✅ New store '{store_name}' added.")



    def add_documents(self, documents, store_type):
        """Adds documents to the vector store, avoiding duplicates by assigning unique IDs."""
        
        if store_type not in self.stores:
            raise ValueError(f"Store '{store_type}' does not exist. Create it first using `add_new_store()`.")

        store = self.stores[store_type]

        # Retrieve existing metadata (which may contain IDs)
        existing_docs = store.get(include=["documents", "metadatas"])
        existing_texts = set(existing_docs.get("documents", []))

        unique_documents = []
        for doc in documents:
            doc_hash = hashlib.md5(doc.page_content.encode()).hexdigest()  # Generate unique hash ID
            if doc.page_content not in existing_texts:
                doc.metadata["id"] = doc_hash  # Assign a unique ID
                unique_documents.append(doc)

        if not unique_documents:
            print(f"✅ No new documents to add in '{store_type}'. Skipping insertion.")
            return

        store.add_documents(unique_documents)
        print(f"✅ Added {len(unique_documents)} new documents to '{store_type}'.")



    def search(self, query, store_type, top_k=5):
        """
        Searches for documents in a specific vector store.

        Args:
            query (str): The search query.
            store_type (str): Name of the store.
            top_k (int): Number of results to return.

        Returns:
            list: Retrieved documents.
        """
        if store_type not in self.stores:
            raise ValueError(f"Store '{store_type}' does not exist.")

        store = self.stores[store_type]
        return store.similarity_search(query, k=top_k)

# Example Usage:
if __name__ == "__main__":
    vector_db = VectorStore()

    # Add a new store dynamically
    vector_db.add_new_store("faculty")
    
    # Example search in the new store
    query = "Who teaches Machine Learning?"
    results = vector_db.search(query, store_type="faculty")

    for doc in results:
        print(f"📌 Retrieved: {doc.page_content}")
