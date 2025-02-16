from langraph_pipeline import build_graph, build_agent_graph
import time

def run_rag_system(input_message, graph, use_agent):
    """Runs the RAG system with user input."""
    print("🔍 Starting query processing...")  
    config = {"configurable": {"thread_id": "abc_123"}}
    if use_agent:
        print("🕵️ Using agent for query processing...")
        response = graph.invoke({"messages": [{"role": "user", "content": input_message}]}, config=config)
    else:
        print("💡 Running standard RAG pipeline...")
        response = graph.invoke({"messages": [{"role": "user", "content": input_message}]})
    

# Extract and print the final response
    
    print(response["messages"][-1].content)



if __name__ == "__main__":

    user_query = input("Enter your query: ")
    print(f"User query received: {user_query}")  # Debugging print
    use_agent = input("Use agent? (yes/no): ").strip().lower() == "yes"
    
    if use_agent:
        graph = build_agent_graph()
    else:
        graph = build_graph()
    run_rag_system(user_query, graph, use_agent)

