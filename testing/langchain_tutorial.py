from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langchain_openai import ChatOpenAI
from IPython.display import Image, display


# 1. Define the State type
class State(TypedDict):
    messages: Annotated[list, add_messages]


# 2. Build the Graph
def build_graph() -> StateGraph:
    graph_builder = StateGraph(State)
    llm = ChatOpenAI(model_name="gpt-4o-mini")

    def chatbot(state: State):
        return {"messages": [llm.invoke(state["messages"])]}

    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)

    return graph_builder.compile()


# 3. Display graph as Mermaid diagram (optional visualization)
def display_graph(graph):
    try:
        display(Image(graph.get_graph().draw_mermaid_png()))
    except Exception:
        print("Graph visualization skipped (optional dependency missing).")


# 4. Function to stream chat output
def stream_graph_updates(graph, user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


# 5. Main chat loop
def main():
    graph = build_graph()
    display_graph(graph)

    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            stream_graph_updates(graph, user_input)
        except:
            # fallback demo message
            user_input = "What do you know about LangGraph?"
            print("User: " + user_input)
            stream_graph_updates(graph, user_input)
            break


# 6. Entry point
if __name__ == "__main__":
    main()
