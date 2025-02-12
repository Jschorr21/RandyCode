from langraph_pipeline import graph
import time

def run_rag_system(input_message):
    """Runs the RAG system with user input."""
    print("🔍 Starting query processing...")  # Debugging print
    for step in graph.stream(
        {"messages": [{"role": "user", "content": input_message}]},
        stream_mode="values",
    ):
        print("Response received!")  # Debugging print
        print(" Assistant's response:", step["messages"][-1].content) 
    time.sleep(10) # Ensures output is printed

if __name__ == "__main__":
    user_query = input("Enter your query: ")
    print(f"User query received: {user_query}")  # Debugging print
    run_rag_system(user_query)
    time.sleep(5)
