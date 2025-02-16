import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
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
            dict: A dictionary with the generated message and sources.
        """
        logging.info("📝 Generating response...")

        # Get retrieved context and sources
        retrieved_data = state.get("messages", [{}])[-1]  # Get last retrieved message
        retrieved_text = retrieved_data.get("content", "")
        sources = retrieved_data.get("sources", [])

        if not retrieved_text:
            logging.warning("⚠️ No retrieved documents found! Returning fallback response.")
            return {"messages": ["I couldn't find relevant information. Please rephrase or ask another question."]}

        system_message_content = SYSTEM_PROMPT_TEMPLATE.format(context=retrieved_text)
        conversation_messages = [SystemMessage(system_message_content)]

        # Call the LLM
        response = self.llm.invoke(conversation_messages)
        logging.info(f"🤖 LLM Response: {response.content}")

        # Append sources to response
        sources_text = "\nSources:\n" + "\n".join(sources) if sources else "No sources available."

        return {"messages": [f"{response.content}\n\n{sources_text}"]}
