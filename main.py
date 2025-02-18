from langchain_pipeline.langraph_pipeline import LangGraphPipeline

def run_rag_system():
    """Runs the RAG chatbot."""
    pipeline = LangGraphPipeline()

    user_query = input("Enter your query: ")
    use_agent = input("Use agent? (yes/no): ").strip().lower() == "yes"

    response = pipeline.run_pipeline(user_query, use_agent)

if __name__ == "__main__":
    run_rag_system()
