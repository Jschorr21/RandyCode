import logging
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import SystemMessage, ToolMessage
from langgraph.graph import MessagesState
from langchain_pipeline.prompts import SYSTEM_PROMPT_TEMPLATE
import json
import re
logging.basicConfig(level=logging.INFO)

class ResponseGenerator:
    """Handles response generation using GPT-4."""

    def __init__(self, llm, user_data_path="./user_profiles.json"):
        """Initialize the response generator with the shared LLM model."""
        self.llm = llm  # ✅ Use the shared LLM instance
        self.user_data_path = user_data_path
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
        user_id = state.get("user_id", "jake")
        user_profile = self.get_user_profile(user_id)

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


        # ✅ Step 2: Collect all retrieval (ToolMessage) results **after** the last AI tool invocation
        latest_retrieved_docs = [
            msg for msg in state["messages"][last_tool_call_index + 1:] if isinstance(msg, ToolMessage)
        ]

        if not latest_retrieved_docs:
            print("⚠️ No new retrieved documents found! Returning fallback response.")
            return {"messages": ["I couldn't find relevant information. Please rephrase or ask another question."]}


        # ✅ Step 3: Concatenate only the latest batch of retrievals
        def strip_docs_list_json(text):
            return re.sub(r"\[DOCS_LIST_JSON_START].*?\[DOCS_LIST_JSON_END\]", "", text, flags=re.DOTALL).strip()

        docs_content = "\n\n".join(
            strip_docs_list_json(doc.content)
            for doc in latest_retrieved_docs
            if doc.content.strip()
        )

        
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

        # ✅ Call LLM with updated prompt
        response = self.llm.invoke(prompt)

        return {"messages": [response]}
    
    def stream_generate(self, state: MessagesState):
        user_id = state.get("user_id", "jake")
        user_profile = self.get_user_profile(user_id)

        last_tool_call_index = None
        for i in reversed(range(len(state["messages"]))):
            message = state["messages"][i]
            if message.type == "ai" and message.tool_calls:
                last_tool_call_index = i
                break

        if last_tool_call_index is None:
            yield "I couldn't find relevant information. Please rephrase or ask another question."
            return

        latest_retrieved_docs = [
            msg for msg in state["messages"][last_tool_call_index + 1:] if isinstance(msg, ToolMessage)
        ]

        if not latest_retrieved_docs:
            yield "I couldn't find relevant information. Please rephrase or ask another question."
            return

        def strip_docs_list_json(text):
            return re.sub(r"\[DOCS_LIST_JSON_START].*?\[DOCS_LIST_JSON_END\]", "", text, flags=re.DOTALL).strip()

        docs_content = "\n\n".join(
            strip_docs_list_json(doc.content)
            for doc in latest_retrieved_docs
            if doc.content.strip()
        )

        conversation_messages = [
            msg for msg in state["messages"]
            if msg.type in ("human", "system") or (msg.type == "ai" and not msg.tool_calls)
        ]

        system_message_content = SYSTEM_PROMPT_TEMPLATE.format(
            context=docs_content,
            question=conversation_messages[-1].content,
            major=user_profile["major"],
            course_history=", ".join(user_profile["course_history"]) or "None"
        )

        prompt = [SystemMessage(system_message_content)] + conversation_messages

        # ✅ Stream from the LLM
        for chunk in self.llm.stream(prompt):
            if chunk.content:
                print(f"chunk: {chunk.content}")
                yield chunk.content

