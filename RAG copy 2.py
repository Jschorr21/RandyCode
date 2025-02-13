{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "os.environ[\"LANGSMITH_API_KEY\"] = \"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\"\n",
    "os.environ[\"LANGCHAIN_API_KEY\"] = \"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\"\n",
    "\n",
    "import getpass\n",
    "\n",
    "if not os.environ.get(\"OPENAI_API_KEY\"):\n",
    "  os.environ[\"OPENAI_API_KEY\"] = getpass.getpass(\"Enter API key for OpenAI: \")\n",
    "\n",
    "from langchain_openai import ChatOpenAI\n",
    "from langchain.chat_models import init_chat_model\n",
    "llm = init_chat_model(\"gpt-4o-mini\", model_provider=\"openai\")\n",
    "\n",
    "\n",
    "if not os.environ.get(\"OPENAI_API_KEY\"):\n",
    "  os.environ[\"OPENAI_API_KEY\"] = getpass.getpass(\"Enter API key for OpenAI: \")\n",
    "\n",
    "from langchain_openai import OpenAIEmbeddings\n",
    "\n",
    "embeddings = OpenAIEmbeddings(model=\"text-embedding-3-large\")\n",
    "\n",
    "\n",
    "from langchain_community.vectorstores import Chroma\n",
    "from langchain.embeddings.openai import OpenAIEmbeddings\n",
    "\n",
    "# Define the storage directory\n",
    "persist_directory = \"./chroma_db\"\n",
    "\n",
    "# Initialize Chroma with persistence\n",
    "catalog_store = Chroma(\n",
    "    collection_name=\"Catalog\",\n",
    "    embedding_function=embeddings,\n",
    "    persist_directory=persist_directory  # Specify where to store the database\n",
    ")\n",
    "courses_store = Chroma(\n",
    "    collection_name=\"Courses\",\n",
    "    embedding_function=embeddings,\n",
    "    persist_directory=persist_directory  # Specify where to store the database\n",
    ")\n",
    "\n",
    "print(f\"ChromaDB is stored at: {persist_directory}\")\n",
    "\n",
    "\n",
    "from langchain_core.prompts import ChatPromptTemplate\n",
    "from langchain import hub\n",
    "prompt = ChatPromptTemplate.from_template(\"You are an assistant meant to help Vanderbilt students with course registration and other relevant Vanderbilt information. Use the following pieces of retrieved context to answer the question. You will not go outside the scope of the retrieved context. If the answer to the question is not present in the retrieved context then reply \\\" That question is outside the scope of my knowledge: try rephrasing.\\\" Keep the answer as concise as possible while still answering the question completely.\\n\\nContext: {context} \\n\\nQuestion: {question} \\n\\nAnswer:\")\n",
    "\n",
    "example_messages = prompt.invoke(\n",
    "    {\"context\": \"(context goes here)\", \"question\": \"(question goes here)\"}\n",
    ").to_messages()\n",
    "assert len(example_messages) == 1\n",
    "print(example_messages[0].content)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "# from langchain_community.document_loaders import PyPDFLoader\n",
    "\n",
    "# # Load the PDF file\n",
    "# pdf_loader = PyPDFLoader(\"Undergraduate_Catalog_2024-25.pdf\")\n",
    "# documents = pdf_loader.load()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# from langchain.text_splitter import RecursiveCharacterTextSplitter\n",
    "\n",
    "# # Initialize the text splitter\n",
    "# text_splitter = RecursiveCharacterTextSplitter(\n",
    "#     chunk_size=1000,  # Number of characters per chunk\n",
    "#     chunk_overlap=300,  # Overlap between chunks\n",
    "# )\n",
    "\n",
    "# # Split the documents\n",
    "# split_documents = text_splitter.split_documents(documents)\n",
    "# print(f\"Split catalog into {len(split_documents)} sub-documents.\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "catalog = catalog_store.get()\n",
    "courses = courses_store.get()\n",
    "for i, metadata in enumerate(courses['metadatas']):\n",
    "    print(f\"\\nDocument {i} metadata:\")\n",
    "    print(metadata)\n",
    "\n",
    "# for i, metadata in enumerate(catalog['metadatas']):\n",
    "#     print(f\"\\nDocument {i} metadata:\")\n",
    "#     print(metadata)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import json\n",
    "from langchain.schema import Document\n",
    "\n",
    "# Load chunks from JSON file\n",
    "with open(\"chunks.json\", \"r\", encoding=\"utf-8\") as file:\n",
    "    chunk_data = json.load(file)  # Parse JSON file\n",
    "\n",
    "# Convert JSON data into LangChain Document objects\n",
    "catalog_documents = [\n",
    "    Document(\n",
    "        page_content=chunk[\"text\"],  # Extract text content\n",
    "        metadata={\"id\": chunk[\"id\"], \"page\": chunk[\"metadata\"][\"page\"], \"source\": \"chunks.json\"}\n",
    "    )\n",
    "    for chunk in chunk_data\n",
    "]\n",
    "\n",
    "print(f\"Loaded {len(catalog_documents)} chunks from chunks.json.\")\n",
    "\n",
    "catalog_document_ids = catalog_store.add_documents(documents=catalog_documents)\n",
    "\n",
    "print(catalog_document_ids[:3])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 111,
   "metadata": {},
   "outputs": [],
   "source": [
    "import csv\n",
    "from langchain_core.documents import Document\n",
    "\n",
    "# DONT NEED TO RERUN\n",
    "def read_csv_to_list(file_path):\n",
    "    documents = []\n",
    "    metadata = []\n",
    "    ids = []\n",
    "    \n",
    "    with open(file_path, newline='', encoding='utf-8') as csvfile:\n",
    "        reader = csv.reader(csvfile)\n",
    "        for i, row in enumerate(reader):\n",
    "            if i >= 1:\n",
    "                page_content = ', '.join(row)  # Convert row to a string\n",
    "                \n",
    "                if len(row) > 1:\n",
    "                    course_code = row[1].split(' -')[0]  # Strip everything including and after '-'\n",
    "                    doc_metadata = {'course_code': course_code, 'subject_area': row[0]}  # Extract cleaned course \n",
    "                    metadata.append(doc_metadata)\n",
    "                \n",
    "                ids.append(f\"doc_{i}\")  # Assign a unique ID to each document\n",
    "                \n",
    "                # Create a Document object with page_content and metadata\n",
    "                documents.append(Document(page_content=page_content, metadata=doc_metadata))\n",
    "\n",
    "    return documents, metadata, ids\n",
    "\n",
    "# Example usage\n",
    "file_path = 'subject_courses.csv'  # Replace with your actual file path\n",
    "course_documents, course_metadata, ids = read_csv_to_list(file_path)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "courses_store.add_documents(documents=course_documents, metadata=course_metadata)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "We'll use LangGraph to tie together the retrieval and generation steps into a single application. This will bring a number of benefits:\n",
    "\n",
    "We can define our application logic once and automatically support multiple invocation modes, including streaming, async, and batched calls.\n",
    "We get streamlined deployments via LangGraph Platform.\n",
    "LangSmith will automatically trace the steps of our application together.\n",
    "We can easily add key features to our application, including persistence and human-in-the-loop approval, with minimal code changes."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "metadata": {},
   "outputs": [],
   "source": [
    "from typing import TypedDict\n",
    "from langchain_core.documents import Document\n",
    "from langchain_core.vectorstores import InMemoryVectorStore\n",
    "from typing_extensions import Annotated\n",
    "\n",
    "\n",
    "class Search(TypedDict):\n",
    "    \"\"\"Search query.\"\"\"\n",
    "    query: Annotated[str, ..., \"Search query to run.\"]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "metadata": {},
   "outputs": [],
   "source": [
    "from langchain_core.documents import Document\n",
    "from typing_extensions import List, TypedDict\n",
    "\n",
    "\n",
    "class State(TypedDict):\n",
    "    question: str\n",
    "    query: Search\n",
    "    context: List[Document]\n",
    "    answer: str"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "The state of our application controls what data is input to the application, transferred between steps, and output by the application. It is typically a TypedDict, but can also be a Pydantic BaseModel.\n",
    "\n",
    "For a simple RAG application, we can just keep track of the input question, retrieved context, and generated answer:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [],
   "source": [
    "def analyze_query(state: State):\n",
    "    structured_llm = llm.with_structured_output(Search)\n",
    "    query = structured_llm.invoke(state[\"question\"])\n",
    "    return {\"query\": query}"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": 95,
   "metadata": {},
   "outputs": [],
   "source": [
    "from langchain_core.tools import tool\n",
    "\n",
    "@tool(response_format=\"content_and_artifact\")\n",
    "def retrieve(query: str):\n",
    "    \"\"\"Retrieve information related to a query.\"\"\"\n",
    "    # Retrieve 4 documents from each collection\n",
    "    catalog_docs = catalog_store.similarity_search(query, k=8)\n",
    "    courses_docs = courses_store.similarity_search(query, k=4)\n",
    "\n",
    "    # Label and retain metadata\n",
    "    labeled_catalog_docs = [\n",
    "    {\n",
    "        \"content\": doc.page_content,\n",
    "        \"source\": doc.metadata.get(\"source\", \"Undergraduate Catalog Information\"),\n",
    "        \"metadata\": doc.metadata  # Retain metadata\n",
    "    }\n",
    "    for doc in catalog_docs\n",
    "    ]\n",
    "\n",
    "    labeled_courses_docs = [\n",
    "    {\n",
    "        \"content\": doc.page_content,\n",
    "        \"source\": doc.metadata.get(\"source\", \"Course Information\"),\n",
    "        \"metadata\": doc.metadata  # Retain metadata\n",
    "    }\n",
    "    for doc in courses_docs\n",
    "    ]\n",
    "\n",
    "    \n",
    "\n",
    "    # Combine results\n",
    "    retrieved_docs = labeled_catalog_docs + labeled_courses_docs\n",
    "\n",
    "    serialized = \"\\n\\n\".join(\n",
    "        (\n",
    "            f\"Source: {doc['source']}\\n\"\n",
    "            f\"Metadata: {doc['metadata']}\\n\"\n",
    "            f\"Content: {doc['content']}\"\n",
    "        )\n",
    "        for doc in retrieved_docs\n",
    "    )\n",
    "\n",
    "    return serialized, retrieved_docs\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 35,
   "metadata": {},
   "outputs": [],
   "source": [
    "from langchain_core.messages import SystemMessage\n",
    "from langgraph.prebuilt import ToolNode\n",
    "\n",
    "\n",
    "# Step 1: Generate an AIMessage that may include a tool-call to be sent.\n",
    "def query_or_respond(state: MessagesState):\n",
    "    \"\"\"Generate tool call for retrieval or respond.\"\"\"\n",
    "    llm_with_tools = llm.bind_tools([retrieve])\n",
    "    response = llm_with_tools.invoke(state[\"messages\"])\n",
    "    # MessagesState appends messages to state instead of overwriting\n",
    "    return {\"messages\": [response]}\n",
    "\n",
    "\n",
    "# Step 2: Execute the retrieval.\n",
    "tools = ToolNode([retrieve])\n",
    "\n",
    "\n",
    "# step 3: generate a response using retrieved context\n",
    "def generate(state: MessagesState):\n",
    "    \"\"\"Generate answer.\"\"\"\n",
    "    # Get generated ToolMessages\n",
    "    recent_tool_messages = []\n",
    "    for message in reversed(state[\"messages\"]):\n",
    "        if message.type == \"tool\":\n",
    "            recent_tool_messages.append(message)\n",
    "        else:\n",
    "            break\n",
    "    tool_messages = recent_tool_messages[::-1]\n",
    "\n",
    "\n",
    "     # Format retrieved documents with labels (like your original code)\n",
    "    docs_content = \"\\n\\n\".join(doc.content for doc in tool_messages)\n",
    "\n",
    "    system_message_content =(\n",
    "        \"You are an assistant meant to help Vanderbilt students with course registration and other relevant Vanderbilt information. Use the following pieces of retrieved context to answer the question. You will not go outside the scope of the retrieved context. If the answer to the question is not present in the retrieved context then reply \\\" That question is outside the scope of my knowledge: try rephrasing.\\\" Keep the answer as concise as possible while still answering the question completely.\\n\\n\"\n",
    "        f\"Context:\\n{docs_content}\"\n",
    "    \n",
    "    )\n",
    "\n",
    "    conversation_messages = [\n",
    "        message\n",
    "        for message in state[\"messages\"]\n",
    "        if message.type in (\"human\", \"system\")\n",
    "        or (message.type == \"ai\" and not message.tool_calls)\n",
    "    ]\n",
    "    prompt = [SystemMessage(system_message_content)] + conversation_messages\n",
    "\n",
    "    # Run\n",
    "    response = llm.invoke(prompt)\n",
    "    return {\"messages\": [response]}\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "retrieve stores retrieved docs from the vector store^"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 129,
   "metadata": {},
   "outputs": [],
   "source": [
    "from langgraph.graph import END\n",
    "from langgraph.prebuilt import ToolNode\n",
    "\n",
    "from langgraph.graph import START, StateGraph, MessagesState\n",
    "\n",
    "graph_builder = StateGraph(MessagesState)\n",
    "\n",
    "graph_builder.add_node(query_or_respond)\n",
    "graph_builder.add_node(tools)\n",
    "graph_builder.add_node(generate)\n",
    "\n",
    "graph_builder.set_entry_point(\"query_or_respond\")\n",
    "graph_builder.add_conditional_edges(\n",
    "    \"query_or_respond\",\n",
    "    tools_condition,\n",
    "    {END: END, \"tools\": \"tools\"},\n",
    ")\n",
    "graph_builder.add_edge(\"tools\", \"generate\")\n",
    "graph_builder.add_edge(\"generate\", END)\n",
    "\n",
    "graph = graph_builder.compile()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 29,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "calls the prompt and passes in the context and question to messages, and sends messages to the llm"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from IPython.display import Image, display\n",
    "\n",
    "display(Image(graph.get_graph().draw_mermaid_png()))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "input_message = \"What are the requirements for the computer science major?\"\n",
    "\n",
    "for step in graph.stream(\n",
    "    {\"messages\": [{\"role\": \"user\", \"content\": input_message}]},\n",
    "    stream_mode=\"values\",\n",
    "):\n",
    "    step[\"messages\"][-1].pretty_print()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 122,
   "metadata": {},
   "outputs": [],
   "source": [
    "from langgraph.checkpoint.memory import MemorySaver\n",
    "\n",
    "\n",
    "#future, use redissaver to keep memory\n",
    "memory = MemorySaver()\n",
    "graph = graph_builder.compile(checkpointer=memory)\n",
    "\n",
    "# Specify an ID for the thread\n",
    "config = {\"configurable\": {\"thread_id\": \"abc123\"}}"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "input_message = \"What are the requirements for the computer science major?\\n\\n Once you get the answer, look up more general information about the major.\"\n",
    "\n",
    "for step in graph.stream(\n",
    "    {\"messages\": [{\"role\": \"user\", \"content\": input_message}]},\n",
    "    stream_mode=\"values\",\n",
    "    config=config\n",
    "):\n",
    "    step[\"messages\"][-1].pretty_print()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "input_message = \"what can i take as depth classes for this major?\"\n",
    "\n",
    "for step in graph.stream(\n",
    "    {\"messages\": [{\"role\": \"user\", \"content\": input_message}]},\n",
    "    stream_mode=\"values\",\n",
    "    config=config,\n",
    "):\n",
    "    step[\"messages\"][-1].pretty_print()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "input_message = \"what did i ask about above?\"\n",
    "\n",
    "for step in graph.stream(\n",
    "    {\"messages\": [{\"role\": \"user\", \"content\": input_message}]},\n",
    "    stream_mode=\"values\",\n",
    "    config=config,\n",
    "):\n",
    "    step[\"messages\"][-1].pretty_print()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 79,
   "metadata": {},
   "outputs": [],
   "source": [
    "\n",
    "from langchain_core.messages import SystemMessage\n",
    "from langgraph.prebuilt import create_react_agent\n",
    "system_message_content =(\n",
    "        \"You are an assistant meant to help Vanderbilt students with course registration and other relevant Vanderbilt information. Use the following pieces of retrieved context to answer the question. You will not go outside the scope of the retrieved context. If the answer to the question is not present in the retrieved context then reply \\\" That question is outside the scope of my knowledge: try rephrasing.\\\" Keep the answer as concise as possible while still answering the question completely.\\n\\n\"\n",
    "       \n",
    "    \n",
    "    )\n",
    "\n",
    "system_message = SystemMessage(system_message_content)\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 130,
   "metadata": {},
   "outputs": [],
   "source": [
    "from langgraph.prebuilt import create_react_agent\n",
    "\n",
    "import logging\n",
    "from langchain_core.callbacks import StdOutCallbackHandler\n",
    "\n",
    "logging.basicConfig(level=logging.DEBUG)\n",
    "\n",
    "handler = StdOutCallbackHandler\n",
    "memory = MemorySaver()\n",
    "agent_executor = create_react_agent(llm, [retrieve], checkpointer=memory)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "print(agent_executor.nodes['agent'].__dict__)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import inspect\n",
    "print(inspect.getsource(retrieve))\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "display(Image(agent_executor.get_graph().draw_mermaid_png()))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 126,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "state object keeping track of everything. retrieve and generate are executed in order and modify the state object. retrieve is connected to the starting point"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "config = {\"configurable\": {\"thread_id\": \"def234\"}}\n",
    "\n",
    "input_message = (\n",
    "    \"What are the requirements for the computer science major?\\n\\n\"\n",
    "    \"Once you get the answer, look up more general information about the major.\"\n",
    ")\n",
    "\n",
    "for event in agent_executor.stream(\n",
    "    {\"messages\": [{\"role\": \"user\", \"content\": input_message}]},\n",
    "    stream_mode=\"values\",\n",
    "    \n",
    "    config=config,\n",
    "):\n",
    "    event[\"messages\"][-1].pretty_print()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "fresh_venv",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
