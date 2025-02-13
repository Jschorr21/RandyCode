from langchain_core.tools import tool
from vectorstore import catalog_store, courses_store
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent


@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve information related to a query."""
    print(f"🔍 Searching for: {query}")  # Debugging print

    catalog_docs = catalog_store.similarity_search(query, k=8)
    courses_docs = courses_store.similarity_search(query, k=4)

    print(f" Found {len(catalog_docs)} catalog docs, {len(courses_docs)} course docs.")  # Log found docs

    if not catalog_docs and not courses_docs:
        print(" No documents found in vector store.")  # Debug if nothing is found
        return "I couldn't find any relevant information in the database.", []

    retrieved_docs = catalog_docs + courses_docs
    serialized = "\n\n".join(
        f"Source: {doc.metadata.get('source', 'Unknown')}\nContent: {doc.page_content}"
        for doc in retrieved_docs
    )

    print(f" Retrieved content:\n{serialized[:500]}...")  # Print first 500 chars for debugging

    return serialized, retrieved_docs



from langgraph.graph import END, StateGraph, MessagesState
from langchain_openai import ChatOpenAI
from prompts import prompt

llm = ChatOpenAI(model_name="gpt-4o-mini",)

def query_or_respond(state: MessagesState):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


llm = ChatOpenAI(model_name="gpt-4o-mini")

def generate(state: MessagesState):
    """Generate a response using retrieved context."""
    print("Generating response...")  # Debugging print

    # Get retrieved context
    retrieved_docs = state.get("messages", [])
    
    # Ensure retrieved_docs is a list of documents, not empty
    if not retrieved_docs:
        print("⚠️ No retrieved documents found! Returning fallback response.")
        return {"messages": ["I couldn't find relevant information. Please rephrase or ask another question."]}

    docs_content = "\n\n".join(doc.content for doc in retrieved_docs)

    system_message_content = (
        "You are an assistant meant to help Vanderbilt students with course registration and other relevant Vanderbilt information. "
        "Use the following retrieved context to answer the question. "
        "If no relevant context is found, say 'I don't have enough information to answer that.'\n\n"
        f"Context:\n{docs_content}"
    )

    conversation_messages = [
        SystemMessage(system_message_content)
    ]

    # Call the LLM
    response = llm.invoke(conversation_messages)
    print(f"🤖 LLM Response: {response.content}")  # Debugging print

    return {"messages": [response]}


def build_graph():
    tools = ToolNode([retrieve])
    graph_builder = StateGraph(MessagesState)
    graph_builder = StateGraph(MessagesState)

    graph_builder.add_node(query_or_respond)
    graph_builder.add_node(tools)
    graph_builder.add_node(generate)

    graph_builder.set_entry_point("query_or_respond")
    graph_builder.add_conditional_edges(
        "query_or_respond",
        tools_condition,
        {END: END, "tools": "tools"},
    )
    graph_builder.add_edge("tools", "generate")
    graph_builder.add_edge("generate", END)

    # memory = MemorySaver()
    graph = graph_builder.compile()
    
    return graph

def build_agent_graph():
    memory = MemorySaver()
    agent_executor = create_react_agent(llm, [retrieve], checkpointer=memory)
    return agent_executor


