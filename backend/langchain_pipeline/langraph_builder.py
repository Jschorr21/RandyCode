from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_pipeline.retrieval import retrieve
from langchain_pipeline.response_generator import ResponseGenerator
import logging
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

logging.basicConfig(level=logging.INFO)


class LangGraphBuilder:
    """Builds the LangChain LangGraph state graph."""

    def __init__(self):
        self.response_generator = ResponseGenerator()
        self.llm = ChatOpenAI(model_name="gpt-4o-mini")
        self.memory = MemorySaver()

    def query_or_respond(self, state: MessagesState):
        """Generate tool call for retrieval or respond."""
        llm_with_tools = self.llm.bind_tools([retrieve])
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    def generate_response(self, state: MessagesState):
        """Generate a response using retrieved context."""
        return self.response_generator.generate(state)

    def build_graph(self):
        """
        Creates a LangGraph state graph for RAG.

        Returns:
            StateGraph: Configured LangGraph pipeline.
        """
        tools = ToolNode([retrieve])
        graph_builder = StateGraph(MessagesState)

        graph_builder.add_node("query_or_respond", self.query_or_respond)
        graph_builder.add_node("tools", tools)
        graph_builder.add_node("generate", self.generate_response)

        graph_builder.set_entry_point("query_or_respond")
        graph_builder.add_conditional_edges(
            "query_or_respond",
            tools_condition,
            {END: END, "tools": "tools"},
        )
        graph_builder.add_edge("tools", "generate")
        graph_builder.add_edge("generate", END)

        return graph_builder.compile(checkpointer=self.memory)
