import os
import getpass

os.environ["LANGSMITH_API_KEY"] = "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"
os.environ["LANGCHAIN_API_KEY"] = "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"

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")
