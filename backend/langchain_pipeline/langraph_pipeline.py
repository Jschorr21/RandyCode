import logging
from langchain_pipeline.langraph_builder import LangGraphBuilder
from langchain_pipeline.agent_graph import AgentGraph
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI
logging.basicConfig(level=logging.INFO)
from langchain_core.messages import HumanMessage, AIMessage
from chatapp.models import Message  # adjust to your app structure

class LangGraphPipeline:
    """Orchestrates RAG system execution."""

    def __init__(self):

        self.llm = ChatOpenAI(model_name="gpt-4o-mini")
        self.langraph_builder = LangGraphBuilder(self.llm)
        self.agent_graph = AgentGraph()

    def hydrate_memory(self, memory, thread_id, messages):
        """
        Load messages into LangGraph memory for a specific thread_id.

        Args:
            memory (MemorySaver): The memory object used by LangGraph.
            thread_id (str): The ID used to identify this memory thread.
            messages (list[dict]): List of messages with 'role' and 'content'.
        """
        formatted = []
        for m in messages:
            if m["role"] == "user":
                formatted.append(HumanMessage(content=m["content"]))
            elif m["role"] == "bot":
                formatted.append(AIMessage(content=m["content"]))
        memory.put({"configurable": {"thread_id": thread_id}}, {"messages": formatted})

    def run_pipeline(self, input_message, use_agent=True, user_id="jake", session_id=None):
        """
        Runs the RAG pipeline.

        Args:
            input_message (str): User's query.
            use_agent (bool): Whether to use the agent setup.

        Returns:
            str: Final response.
        """
        logging.info(f"🚀 Running {'Agent' if use_agent else 'Standard'} RAG Pipeline")

        if use_agent:
            graph = self.agent_graph.build_agent_graph()
            response = graph.invoke(
                {"user_id": user_id, "messages": [{"role": "user", "content": input_message}]},
                config={"configurable": {"thread_id": "abc_123"}}  # ✅ Pass only here
            )
            # print(f"\n\n 📝 Response: {response["messages"][-1].content}")
            
            # input_message = input("Enter your query: ")
        else:
            thread_id = session_id or "default"
            graph = self.langraph_builder.build_graph()
            memory = self.langraph_builder.memory
            # 🔁 Hydrate LangGraph memory from DB
            if session_id:
                stored_messages = Message.objects.filter(session__session_id=session_id).order_by("created_at")
                chat_history = [{"role": m.role, "content": m.content} for m in stored_messages]
                self.hydrate_memory(memory, thread_id, chat_history)

            # 🧠 Run the graph
            response = graph.invoke(
                {"messages": [{"role": "user", "content": input_message}]},
                config={"configurable": {"thread_id": thread_id}}
            )

        return response["messages"][-1].content
