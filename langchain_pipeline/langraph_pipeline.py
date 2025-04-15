import logging
from langchain_pipeline.langraph_builder import LangGraphBuilder
from langchain_pipeline.agent_graph import AgentGraph
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI
logging.basicConfig(level=logging.INFO)

class LangGraphPipeline:
    """Orchestrates RAG system execution."""

    def __init__(self):

        self.llm = ChatOpenAI(model_name="gpt-4o-mini")
        self.langraph_builder = LangGraphBuilder(self.llm)
        self.agent_graph = AgentGraph()

    def run_pipeline(self, input_message, use_agent=True, user_id="jake"):
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
            graph = self.langraph_builder.build_graph()
            memory = self.langraph_builder.memory
            response = graph.invoke({"messages": [{"role": "user", "content": input_message}]}, config={"configurable": {"thread_id": "abc_456"}})  # ✅ Standard RAG
            print(f"\n\n 📝 Response: {response["messages"][-1].content}")
            # input_message = input("Enter your query: ")
            state = memory.get({"configurable": {"thread_id": "abc_456"}})

        return response["messages"][-1].content, state
        # return response["messages"][-1].content #use this when using agent