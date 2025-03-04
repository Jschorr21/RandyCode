import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, ToolMessage
from langgraph.graph import MessagesState
from langchain_pipeline.prompts import SYSTEM_PROMPT_TEMPLATE
import json

logging.basicConfig(level=logging.INFO)

class ResponseGenerator:
    """Handles response generation using GPT-4."""

    def __init__(self, user_data_path="./user_profiles.json"):
        """Initialize the response generator with the LLM model."""
        self.llm = ChatOpenAI(model_name="gpt-4o-mini")
        self.user_data_path=user_data_path
        self.user_profiles = self.load_user_profiles()
    def load_user_profiles(self):
        """Load user profiles from a JSON file."""
        try:
            with open(self.user_data_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            logging.warning("User profiles file not found. Creating an empty profile store.")
            return {}
    
    def get_user_profile(self, user_id):
        """Retrieve user profile from loaded data or return default profile."""
    
        return self.user_profiles.get(user_id, {
            "major": "Computer Science",
        "course_history": ["CS1101", "MATH1301", "ASTR1010"]
        })

    def generate(self, state: MessagesState):
        """
        Generates a response using retrieved context.

        Args:
            state (MessagesState): The state containing messages.

        Returns:
            dict: A dictionary with the generated message.
        """
        print("Generating response...")  # ✅ Debugging print
        user_id = state.get("user_id", "jake")
        user_profile = self.get_user_profile(user_id)
        print(user_id)
        print(user_profile)

        # ✅ Extract only tool messages (retrieval results)
        retrieved_docs = [
            message for message in state["messages"] if isinstance(message, ToolMessage)
        ]

        # ✅ Ensure retrieved_docs has valid content
        if not retrieved_docs:
            print("⚠️ No retrieved documents found! Returning fallback response.")
            return {"messages": ["I couldn't find relevant information. Please rephrase or ask another question."]}

        # ✅ Extract clean document content (avoid raw object representations)
        docs_content = "\n\n".join(message.content for message in retrieved_docs if message.content.strip())

        # ✅ Get conversation history excluding tool calls
        conversation_messages = [
            message
            for message in state["messages"]
            if message.type in ("human", "system") or (message.type == "ai" and not message.tool_calls)
        ]

        system_message_content = SYSTEM_PROMPT_TEMPLATE.format(
            context=docs_content,
            question=conversation_messages[-1].content,
            major=user_profile["major"],
            course_history=", ".join(user_profile["course_history"]) or "None"
        )

        prompt = [SystemMessage(system_message_content)] + conversation_messages

        print("\n\nCALLING LLM")
        response = self.llm.invoke(prompt)
        print("\n\nLLM RESPONSE")

        return {"messages": [response]}
