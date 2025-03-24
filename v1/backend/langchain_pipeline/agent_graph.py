from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_pipeline.retrieval import retrieve
from langchain_openai import ChatOpenAI


class AgentGraph:
    """Builds a ReAct agent graph with memory."""

    def __init__(self):
        self.memory = MemorySaver()
        self.llm = ChatOpenAI(model_name="gpt-4o-mini")

    def build_agent_graph(self):
        """
        Creates a ReAct agent setup.

        Returns:
            AgentExecutor: Configured ReAct agent.
        """
        print("Building agent graph...")
        agent_executor = create_react_agent(
            self.llm, [retrieve], checkpointer=self.memory
        )
        return agent_executor
