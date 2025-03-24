from data_ingestion.vector_store import VectorStore
from langchain_core.tools import tool
import logging 
logging.basicConfig(level=logging.INFO)

@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve information related to a query."""
    print(f"🔍 Searching for: {query}")
    vector_store = VectorStore()

    catalog_docs = vector_store.search(query, "catalog", top_k=8)
    courses_docs = vector_store.search(query, "courses", top_k=8)
    website_docs = vector_store.search(query, "websites", top_k=8)

    print(f"📌 Found {len(catalog_docs)} catalog docs, {len(courses_docs)} course docs, and {len(website_docs)} website docs.")

    if not catalog_docs and not courses_docs:
        print("❌ No relevant documents found.")
        return {"content": "I couldn't find any relevant information in the database.", "sources": []}
    
    def format_docs(docs, source_label):
        return [
            f"Source: {source_label}\nContent: {doc.page_content}"
            for doc in docs
        ]

    def format_website_docs(docs):
        return [
            f"Source: Vanderbilt Websites\nURL: {doc.metadata.get('source', 'Unknown')}\nContent: {doc.page_content}"
            for doc in docs
        ]
    catalog_content = format_docs(catalog_docs, "Vanderbilt Undergraduate Catalog")
    courses_content = format_docs(courses_docs, "Vanderbilt Course Descriptions")
    websites_content = format_website_docs(website_docs)
    
    serialized_content = "\n\n".join(catalog_content + courses_content + websites_content)
    sources = list(set(
        f"{doc.metadata.get('source', 'Unknown')} (Page {doc.metadata.get('page', 'N/A')})"
        for doc in catalog_docs + courses_docs + website_docs
    ))
    
    print(f"📂 Retrieved {len(catalog_docs + courses_docs + website_docs)} documents.")
    return serialized_content, sources

        