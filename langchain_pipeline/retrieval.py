from data_ingestion.vector_store import VectorStore
from langchain_core.tools import tool
import logging 
import json

logging.basicConfig(level=logging.INFO)

@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve relevant information to a query from the Vanderbilt catalog, course listings, and websites."""
    print(f"🔍 Searching for: {query}")
    vector_store = VectorStore()

    # Retrieve (doc, score) pairs
    catalog_docs_with_scores = vector_store.search(query, "catalog", top_k=20)
    courses_docs_with_scores = vector_store.search(query, "courses", top_k=20)
    website_docs_with_scores = vector_store.search(query, "websites", top_k=20)

    print(f"📌 Found {len(catalog_docs_with_scores)} catalog docs, "
          f"{len(courses_docs_with_scores)} course docs, and "
          f"{len(website_docs_with_scores)} website docs.")

    if not catalog_docs_with_scores and not courses_docs_with_scores and not website_docs_with_scores:
        print("❌ No relevant documents found.")
        return {"content": "I couldn't find any relevant information in the database.", "sources": []}

    # Combine and sort all by score (lower = more relevant)
    all_docs_with_scores = (
        [(doc, score, "Vanderbilt Undergraduate Catalog") for doc, score in catalog_docs_with_scores] +
        [(doc, score, "Vanderbilt Course Descriptions") for doc, score in courses_docs_with_scores] +
        [(doc, score, "Vanderbilt Websites") for doc, score in website_docs_with_scores]
    )
    top_docs = sorted(all_docs_with_scores, key=lambda x: x[1])[:25]  # Top 15 most relevant

    # Print debug info
    # print(f"\n📊 Selected Top {len(top_docs)} Most Relevant Documents:")
    # for i, (doc, score, source_label) in enumerate(top_docs):
    #     print(f"\n📄 Document {i + 1} | Score: {score:.4f}")
    #     print(f"Source: {source_label}")
    #     print(f"ID: {doc.metadata.get('id', 'No ID')}")
    #     print(f"Content:\n{doc.page_content[:500]}...")  # Optional: trim content in console
    #     print("-" * 80)

    # Format output for system
    def format_doc(doc, source_label):
        if source_label == "Vanderbilt Websites":
            return f"Source: {source_label}\nURL: {doc.metadata.get('source', 'Unknown')}\nContent: {doc.page_content}"
        return f"Source: {source_label}\nContent: {doc.page_content}"

    formatted_docs = [format_doc(doc, source_label) for doc, _, source_label in top_docs]

    serialized_content = "\n\n".join(formatted_docs)
    sources = list(set(
        f"{doc.metadata.get('source', 'Unknown')} (Page {doc.metadata.get('page', 'N/A')})"
        for doc, _, _ in top_docs
    ))

    # For eval script
    encoded = json.dumps(formatted_docs)
    combined = f"[DOCS_LIST_JSON_START]{encoded}[DOCS_LIST_JSON_END]\n\n{serialized_content}"

    return combined, {"sources": sources}
