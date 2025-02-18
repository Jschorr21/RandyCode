from langchain_pipeline.retrieval import retrieve
import logging

logging.basicConfig(level=logging.DEBUG)

def test_retriever():
    """Test the Retriever tool manually."""


    print("\n🧪 Running Test: Valid Query")
    query = "What are the prerequisites for CS 1301?"
    
    # ✅ Use `.invoke()` to call the tool correctly
    response = retrieve.invoke({"query": query})  
    
    print(f"📜 Response: {response['content'][:500]}")
    print(f"📌 Sources: {response['sources']}\n")

if __name__ == "__main__":
    test_retriever()
