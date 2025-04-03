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
from langchain_core.messages import SystemMessage
from langchain_pipeline.prompts import SYSTEM_PROMPT_TEMPLATE, DECISION_SYSTEM_PROMPT, NO_CONTEXT_SYSTEM_PROMPT  # Assuming you have this
import re

class LangGraphBuilder:
    """Builds the LangChain LangGraph state graph."""

    def __init__(self, llm):
        self.response_generator = ResponseGenerator(llm)  # ✅ Pass the shared LLM instance
        self.llm = llm  # ✅ Store the shared instance
        self.memory = MemorySaver()

    

    from langchain_core.messages import SystemMessage

    def query_or_respond(self, state: MessagesState):
        """Generate tool calls for retrieval or generate final response if no tool is needed."""
        llm_with_tools = self.llm.bind_tools([retrieve])

        # Insert decision system prompt first
        decision_prompt = SystemMessage(content=DECISION_SYSTEM_PROMPT)
        decision_input = [decision_prompt] + state["messages"]
        decision_response = llm_with_tools.invoke(decision_input)

        # Check if any tool calls were made
        tool_calls = decision_response.tool_calls
        if tool_calls:
            # Use retrieve
            return {"messages": [decision_response]}
        else:
            # Use the fallback no-context assistant identity prompt
            print("⚠️ No tool calls — re-invoking with NO_CONTEXT_SYSTEM_PROMPT")

            system_prompt = SystemMessage(NO_CONTEXT_SYSTEM_PROMPT)
            conversation_messages = [
                msg for msg in state["messages"]
                if msg.type in ("human", "system") or (msg.type == "ai" and not msg.tool_calls)
            ]
            full_prompt = [system_prompt] + conversation_messages
            print("\n🧠 LLM FINAL PROMPT (NO CONTEXT):")
            for msg in full_prompt:
                print(f"{msg.type.upper()}: {msg.content}\n")
            response = self.llm.invoke(full_prompt)

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
