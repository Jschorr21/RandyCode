import logging
from langchain_pipeline.langraph_builder import LangGraphBuilder
from langchain_pipeline.agent_graph import AgentGraph
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI
logging.basicConfig(level=logging.INFO)
from langchain_core.messages import HumanMessage, AIMessage
from chatapp.models import Message  # adjust to your app structure
from langgraph.checkpoint.memory import MemorySaver


class LangGraphPipeline:
    """Orchestrates RAG system execution."""

    def __init__(self):

        self.llm = ChatOpenAI(model_name="gpt-4o-mini", streaming=True)
        self.memory = MemorySaver()
        self.langraph_builder = LangGraphBuilder(self.llm, memory=self.memory)
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
        self.memory.put({"configurable": {"thread_id": thread_id}}, {"messages": formatted})

    def run_pipeline(self, input_message, use_agent=True, user_id="jake", session_id=None):
        """
        Runs the RAG pipeline.

        Args:
            input_message (str): User's query.
            use_agent (bool): Whether to use the agent setup.

        Returns:
            str: Final response.
        """

        print(f"User message: {input_message}")

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
                chat_history = [{"role": m.sender, "content": m.text} for m in stored_messages]
                if chat_history:
                    self.hydrate_memory(memory, thread_id, chat_history)

            hydrated = memory.get({"configurable": {"thread_id": thread_id}}) or {}
            initial_messages = hydrated.get("messages", [])
            all_messages = initial_messages + [{"role": "user", "content": input_message}]


            response = graph.stream(
                {"messages": all_messages},
                config={"configurable": {"thread_id": thread_id}},
            )


        return response["messages"][-1].content
        
    def stream_pipeline(self, input_message, use_agent=True, user_id="jake", session_id=None):
        if use_agent:
            graph = self.agent_graph.build_agent_graph()
            stream = graph.stream(
                {"user_id": user_id, "messages": [{"role": "user", "content": input_message}]},
                config={"configurable": {"thread_id": "abc_123"}}
            )
        else:
            thread_id = session_id or "default"
            graph = self.langraph_builder.build_graph()
            memory = self.langraph_builder.memory

            if session_id:
                stored_messages = Message.objects.filter(session__session_id=session_id).order_by("created_at")
                chat_history = [{"role": m.sender, "content": m.text} for m in stored_messages]
                if chat_history:
                    self.hydrate_memory(memory, thread_id, chat_history)

            hydrated = memory.get({"configurable": {"thread_id": thread_id}}) or {}
            initial_messages = hydrated.get("messages", [])
            all_messages = initial_messages + [{"role": "user", "content": input_message}]

            stream = graph.stream(
                {"messages": all_messages},
                config={"configurable": {"thread_id": thread_id}},
            )

        for chunk in stream:
            # ✅ Try OpenAI-style delta
            if "choices" in chunk:
                delta = chunk["choices"][0]["delta"]
                content = delta.get("content")
                if content:
                    yield content

            # ✅ Try LangGraph agent-style
            elif "agent" in chunk and "messages" in chunk["agent"]:
                messages = chunk["agent"]["messages"]
                if messages and hasattr(messages[0], "content"):
                    content = messages[0].content
                    if content:
                        yield content

