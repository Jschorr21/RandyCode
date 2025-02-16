from data_ingestion.vector_store import VectorStore
from langchain_core.tools import tool
import logging

logging.basicConfig(level=logging.INFO)

class Retriever:
    """Handles query retrieval from vector stores."""

    def __init__(self):
        self.vector_db = VectorStore()

    @tool(response_format="content_and_artifact")
    def retrieve(self, query: str):
        """Retrieve information related to a query and return sources."""
        logging.debug(f"🔍 Searching for: {query}")

        catalog_docs = self.vector_db.search(query, store_type="catalog")
        courses_docs = self.vector_db.search(query, store_type="courses")

        if not catalog_docs and not courses_docs:
            print("❌ No relevant documents found.")
            return {"content": "I couldn't find any relevant information in the database.", "sources": []}

        retrieved_docs = catalog_docs + courses_docs
        serialized_content = "\n\n".join(
            f"Source: {doc.metadata.get('source', 'Unknown')} | Page: {doc.metadata.get('page', 'N/A')}\nContent: {doc.page_content}"
            for doc in retrieved_docs
        )

        sources = list(set(
            f"{doc.metadata.get('source', 'Unknown')} (Page {doc.metadata.get('page', 'N/A')})"
            for doc in retrieved_docs
        ))

        logging.info(f"📂 Retrieved {len(retrieved_docs)} documents.")

        return {"content": serialized_content, "sources": sources}