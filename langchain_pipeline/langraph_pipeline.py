import logging
from langchain_pipeline.langraph_builder import LangGraphBuilder
from langchain_pipeline.agent_graph import AgentGraph
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI

logging.basicConfig(level=logging.INFO)

class LangGraphPipeline:
    """Orchestrates RAG system execution."""

    def __init__(self):
        self.llm = ChatOpenAI(model_name="gpt-4.1-mini")
        self.langraph_builder = LangGraphBuilder(self.llm)
        self.agent_graph = AgentGraph()

    def run_pipeline(self, input_message, use_agent=False, user_id="jake", thread_id="Abc_123"):
        """
        Runs the RAG pipeline.

        Args:
            input_message (str): User's query.
            use_agent (bool): Whether to use the agent setup.
            user_id (str): Unique session identifier (e.g., chat_id)

        Returns:
            str: Final response.
        """
        logging.info(f"🚀 Running {'Agent' if use_agent else 'Standard'} RAG Pipeline with thread_id={user_id}")

        # if use_agent:
        #     graph = self.agent_graph.build_agent_graph()
        #     response = graph.invoke(
        #         {"user_id": user_id, "messages": [{"role": "user", "content": input_message}]},
        #         config={"configurable": {"thread_id": thread_id}}
        #     )
        # else:
        graph = self.langraph_builder.build_graph()
        memory = self.langraph_builder.memory
        response = graph.invoke(
            {"messages": [{"role": "user", "content": input_message}]},
            config={"configurable": {"thread_id": user_id}}
        )
        state = memory.get({"configurable": {"thread_id": thread_id}})
        return response["messages"][-1].content

        return response["messages"][-1].content, None  # for agent path
