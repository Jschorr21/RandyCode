from data_ingestion.vector_store import VectorStore

vector_db = VectorStore()  # ✅ Uses existing database

# ✅ Check stored data
catalog_data = vector_db.stores["catalog"].get()
courses_data = vector_db.stores["courses"].get()

print(f"📂 Catalog store contains {len(catalog_data['documents'])} documents")
print(f"📂 Courses store contains {len(courses_data['documents'])} documents")

# ✅ Try a sample query
query = "math 1301"
results = vector_db.search(query, store_type="catalog")

print("\n🔍 Sample Search Results:")
for doc in results:
    print(f"📜 {doc.page_content}")
