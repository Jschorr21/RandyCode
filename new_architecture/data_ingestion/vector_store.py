import os
import getpass
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

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
        }

        print(f"✅ ChromaDB initialized at: {self.persist_directory}")

    def _set_env_variables(self):
        """Sets API keys dynamically."""

        if not os.environ.get("LANGSMITH_API_KEY"):
            os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter API key for Langsmith: ")

        if not os.environ.get("LANGCHAIN_API_KEY"):
            os.environ["LANGCHAIN_API_KEY"] = getpass.getpass("Enter API key for Langchain: ")

        if not os.environ.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

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
        """
        Adds documents to the specified vector store.

        Args:
            documents (list): List of LangChain Document objects.
            store_type (str): Name of the store (e.g., "faculty").
        """
        if store_type not in self.stores:
            raise ValueError(f"Store '{store_type}' does not exist. Create it first using `add_new_store()`.")

        store = self.stores[store_type]
        store.add_documents(documents=documents)
        store.persist()
        print(f"✅ {len(documents)} documents added to {store_type} store.")

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
