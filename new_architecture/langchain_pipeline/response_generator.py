import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, ToolMessage
from langgraph.graph import MessagesState
from langchain_pipeline.prompts import SYSTEM_PROMPT_TEMPLATE

logging.basicConfig(level=logging.INFO)

class ResponseGenerator:
    """Handles response generation using GPT-4."""

    def __init__(self):
        """Initialize the response generator with the LLM model."""
        self.llm = ChatOpenAI(model_name="gpt-4o-mini")

    def generate(self, state: MessagesState):
        """
        Generates a response using retrieved context.

        Args:
            state (MessagesState): The state containing messages.

        Returns:
            dict: A dictionary with the generated message.
        """
        print("Generating response...")  # ✅ Debugging print

        # ✅ Get retrieved documents (ensures we extract content properly)
        retrieved_docs = state.get("messages", [])

        # ✅ Ensure retrieved_docs is a list and contains valid content
        if not retrieved_docs:
            print("⚠️ No retrieved documents found! Returning fallback response.")
            return {"messages": ["I couldn't find relevant information. Please rephrase or ask another question."]}

        # ✅ Extract content from ToolMessages properly
        docs_content = "\n\n".join(
            doc.content if isinstance(doc, ToolMessage) else str(doc) for doc in retrieved_docs
        )

        system_message_content = SYSTEM_PROMPT_TEMPLATE.format(context=docs_content)
        conversation_messages = [SystemMessage(system_message_content)]

        # ✅ Call the LLM
        response = self.llm.invoke(conversation_messages)
        print(f"🤖 LLM Response: {response.content}")  # ✅ Debugging print

        return {"messages": [response]}
