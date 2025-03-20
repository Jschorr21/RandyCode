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
        Generates a response using only the latest retrieved context.
        Ensures that multiple retrieval tool calls in the latest step are included.
        """
        print("Generating response...")  # ✅ Debugging print
        user_id = state.get("user_id", "jake")
        user_profile = self.get_user_profile(user_id)
        
        print(f"🔹 User ID: {user_id}")
        print(f"🔹 User Profile: {user_profile}")

        # ✅ Step 1: Identify the last AI-generated tool invocation
        last_tool_call_index = None
        for i in reversed(range(len(state["messages"]))):
            message = state["messages"][i]
            if message.type == "ai" and message.tool_calls:
                last_tool_call_index = i
                break  # Found the last AI tool call, stop searching

        if last_tool_call_index is None:
            print("⚠️ No tool calls found in recent history. Returning fallback response.")
            return {"messages": ["I couldn't find relevant information. Please rephrase or ask another question."]}

        print(f"🔍 Last tool invocation found at index: {last_tool_call_index}")

        # ✅ Step 2: Collect all retrieval (ToolMessage) results **after** the last AI tool invocation
        latest_retrieved_docs = [
            msg for msg in state["messages"][last_tool_call_index + 1:] if isinstance(msg, ToolMessage)
        ]

        if not latest_retrieved_docs:
            print("⚠️ No new retrieved documents found! Returning fallback response.")
            return {"messages": ["I couldn't find relevant information. Please rephrase or ask another question."]}

        print(f"📂 Retrieved {len(latest_retrieved_docs)} document(s) in latest step.")

        # ✅ Step 3: Concatenate only the latest batch of retrievals
        docs_content = "\n\n".join(doc.content for doc in latest_retrieved_docs if doc.content.strip())

        print(f"📜 Context length: {len(docs_content)} characters")
        
        # ✅ Step 4: Extract conversation history (excluding tool messages)
        conversation_messages = [
            msg for msg in state["messages"]
            if msg.type in ("human", "system") or (msg.type == "ai" and not msg.tool_calls)
        ]

        # ✅ Step 5: Update system message to include ONLY latest retrieved docs
        system_message_content = SYSTEM_PROMPT_TEMPLATE.format(
            context=docs_content,  # Use only the latest retrieval batch
            question=conversation_messages[-1].content,
            major=user_profile["major"],
            course_history=", ".join(user_profile["course_history"]) or "None"
        )

        prompt = [SystemMessage(system_message_content)] + conversation_messages

        # ✅ Debugging: Print exactly what is sent to the LLM
        formatted_prompt = "\n\n".join(f"{msg.type.upper()}: {msg.content}" for msg in prompt)

        print("\n\n📩 FINAL PROMPT SENT TO LLM:\n", formatted_prompt)
        print(f"\n\n📝 PROMPT SIZE: {len(formatted_prompt)} characters\n\n")

        # ✅ Call LLM with updated prompt
        print("🧠 CALLING LLM")
        response = self.llm.invoke(prompt)
        print("💡 LLM RESPONSE RECEIVED")

        return {"messages": [response]}
