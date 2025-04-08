from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_pipeline.retrieval import retrieve
from langchain_pipeline.response_generator import ResponseGenerator
import logging
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import ToolMessage
logging.basicConfig(level=logging.INFO)
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_pipeline.prompts import SYSTEM_PROMPT_TEMPLATE, DECISION_SYSTEM_PROMPT, NO_CONTEXT_SYSTEM_PROMPT  # Assuming you have this
import re

class LangGraphBuilder:
    """Builds the LangChain LangGraph state graph."""

    def __init__(self, llm):
        self.response_generator = ResponseGenerator(llm)  # ✅ Pass the shared LLM instance
        self.llm = llm  # ✅ Store the shared instance
        self.memory = MemorySaver()

    

    from langchain_core.messages import SystemMessage
    

    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
    def query_or_respond(self, state: MessagesState):
        """Generate tool calls for retrieval or respond, tracking retrieval count."""
        llm_with_tools = self.llm.bind_tools([retrieve])

        # ✅ Count existing retrieval tool messages
        previous_retrievals = sum(1 for message in state["messages"] if isinstance(message, ToolMessage))
        
        # ✅ Invoke LLM with tools
        response = llm_with_tools.invoke(state["messages"])
        
        # ✅ Track the number of retrieve calls made in THIS query step
        new_retrievals = sum(1 for message in response.additional_kwargs.get("messages", []) if message.type == "tool")
        
        # ✅ Store count in state
        state["retrieve_count"] = new_retrievals - previous_retrievals

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
