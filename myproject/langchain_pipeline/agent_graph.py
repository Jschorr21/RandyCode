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
        prompt = """
        You are a helpful assistant meant to answer questions from Vanderbilt students about course registration and other relevant Vanderbilt information. You are provided with context from a few different information sources that you will use to help answer the question. The information sources are the following:\n\n
        Vanderbilt Undergraduate Catalog: This source is the official academic resource detailing degree programs, major and minor requirements, faculty, academic policies, and university regulations. It provides authoritative and structured information on the curriculum, including prerequisites, credit hours, and graduation requirements. This source should be prioritized for official academic guidance and degree planning.\n\n
        Vanderbilt Course Descriptions: This source includes the official descriptions of all offered courses across various departments. These descriptions typically outline course objectives, topics covered, instructional methods, and any prerequisites. These descriptions serve as a reliable reference for understanding course content and academic focus.\n\n
        Vanderbilt Public Domain Information: This source includes publicly available university resources, such as Vanderbilt’s website and any subdomains, faculty directories, departmental pages, and official announcements. It may contain information about campus resources, admissions, tuition, faculty research, student organizations, and policies. This data is useful for general Vanderbilt-related inquiries beyond courses and academics.\n\n
        Use the following retrieved context to answer the question. Do not go outside the scope of the retrieved context. If the answer is not present in the context, respond with: 'That question is outside the scope of my knowledge. Try rephrasing.’\n\n"""

        print("Building agent graph...")
        agent_executor = create_react_agent(self.llm, [retrieve], checkpointer=self.memory, prompt=prompt)
        return agent_executor