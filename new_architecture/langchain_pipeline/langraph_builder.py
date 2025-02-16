from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_pipeline.retrieval import Retriever
from langchain_pipeline.response_generator import ResponseGenerator
import logging

logging.basicConfig(level=logging.INFO)

class LangGraphBuilder:
    """Builds the LangChain LangGraph state graph."""

    def __init__(self):
        self.retriever = Retriever()
        self.response_generator = ResponseGenerator()

    def query_or_respond(self, state: MessagesState):
        """Call retrieval tool before generating response."""
        user_message = state["messages"][-1]  # Get last user query
        query = user_message["content"] if isinstance(user_message, dict) else user_message
        
        logging.info(f"🔍 Running retrieval step for: {query}")
        retrieval_result = self.retriever.retrieve(query)

        return {"messages": [retrieval_result]}  # ✅ Ensure retrieval happens first

    def generate_response(self, state: MessagesState):
        """Generate a response using retrieved context."""
        return self.response_generator.generate(state)

    def build_graph(self):
        """
        Creates a LangGraph state graph for RAG.

        Returns:
            StateGraph: Configured LangGraph pipeline.
        """
        tools = ToolNode([self.retriever.retrieve])
        graph_builder = StateGraph(MessagesState)

        graph_builder.add_node("query_or_respond", self.query_or_respond)
        graph_builder.add_node("tools", tools)
        graph_builder.add_node("generate", self.generate_response)

        graph_builder.set_entry_point("query_or_respond")
        graph_builder.add_edge("query_or_respond", "tools")  # ✅ Ensure retrieval tool runs first
        graph_builder.add_edge("tools", "generate")
        graph_builder.add_edge("generate", END)

        return graph_builder.compile()
