# backend/chatapp/utils/langchain_bridge.py

from langchain_pipeline.langraph_pipeline import LangGraphPipeline

pipeline = LangGraphPipeline()

def get_response_from_pipeline(message: str):
    return pipeline.run_pipeline(message, use_agent=False)