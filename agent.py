import logging
from langgraph.prebuilt import create_react_agent
from retrieval import retrieve
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

llm = ChatOpenAI(model_name="gpt-4o-mini", model_provider="openai")

logging.basicConfig(level=logging.DEBUG)
memory = MemorySaver()

agent_executor = create_react_agent(llm, [retrieve], checkpointer=memory)
