import matplotlib.pyplot as plt
from data_ingestion.vector_store import VectorStore
from langchain_pipeline.retrieval import retrieve
from langchain_pipeline.langraph_builder import LangGraphBuilder
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI

def plot_scores(scores, title):
    if scores:
        plt.figure(figsize=(8, 4))
        plt.plot(sorted(scores), marker='o')
        plt.title(f"{title} (Lower = More Relevant)")
        plt.xlabel("Document Rank")
        plt.ylabel("Distance Score")
        plt.grid(True)
        plt.show()

def print_docs_with_scores(docs_with_scores, store_name):
    if docs_with_scores:
        print(f"\n📚 {store_name.upper()} DOCUMENTS AND SCORES:")
        for i, (doc, score) in enumerate(docs_with_scores):
            print(f" {i + 1}. Score: {score:.4f}")
            print(f"    Content: {doc.page_content}...")  # Limit content length
            print("-" * 80)
    else:
        print(f"\n📚 No documents found for {store_name}.")

def run_query_to_retrieval_query(user_query: str):
    llm = ChatOpenAI(model="gpt-4o-mini")
    builder = LangGraphBuilder(llm)
    state = {"messages": [HumanMessage(content=user_query)]}
    result = builder.query_or_respond(state)
    messages = result["messages"]

    for message in messages:
        if hasattr(message, "tool_calls") and message.tool_calls:
            for call in message.tool_calls:
                if call["name"] == "retrieve":
                    return call["args"]["query"]
    return user_query  # Fallback if no tool call was generated

def retrieve_and_plot_with_langraph_query(query: str, top_k=25):
    vector_store = VectorStore()

    print(f"\n🔍 Original query: '{query}'")
    retrieval_query = run_query_to_retrieval_query(query)
    print(f"🔁 Transformed to retrieval query: '{retrieval_query}'")

    # Retrieve (doc, score) tuples from each store
    catalog_docs_with_scores = vector_store.search(retrieval_query, "catalog", top_k=top_k)
    courses_docs_with_scores = vector_store.search(retrieval_query, "courses", top_k=top_k)
    website_docs_with_scores = vector_store.search(retrieval_query, "websites", top_k=top_k)

    # Print documents and scores
    print_docs_with_scores(catalog_docs_with_scores, "catalog")
    print_docs_with_scores(courses_docs_with_scores, "courses")
    print_docs_with_scores(website_docs_with_scores, "websites")

    # Unpack scores and track sources
    all_scores = []
    all_sources = []

    for score_pair in catalog_docs_with_scores:
        all_scores.append(score_pair[1])
        all_sources.append("Catalog")

    for score_pair in courses_docs_with_scores:
        all_scores.append(score_pair[1])
        all_sources.append("Courses")

    for score_pair in website_docs_with_scores:
        all_scores.append(score_pair[1])
        all_sources.append("Websites")

    # Plot individual score distributions
    plot_scores([s for _, s in catalog_docs_with_scores], "Catalog Document Scores")
    plot_scores([s for _, s in courses_docs_with_scores], "Courses Document Scores")
    plot_scores([s for _, s in website_docs_with_scores], "Website Document Scores")

    # Plot combined with color coding
        # Combined plot with sorted scores and connected lines
    if all_scores:
        # Zip, sort by score
        sorted_scores_with_sources = sorted(zip(all_scores, all_sources), key=lambda x: x[0])
        sorted_scores = [s for s, _ in sorted_scores_with_sources]
        sorted_sources = [src for _, src in sorted_scores_with_sources]

        # Color mapping
        color_map = {"Catalog": "blue", "Courses": "green", "Websites": "orange"}
        colors = [color_map[src] for src in sorted_sources]

        # Plot
        plt.figure(figsize=(10, 5))
        for i in range(len(sorted_scores) - 1):
            plt.plot([i, i+1], [sorted_scores[i], sorted_scores[i+1]], color=colors[i])
        plt.scatter(range(len(sorted_scores)), sorted_scores, c=colors)

        plt.title("Combined Document Scores by Source (Sorted, Lower = More Relevant)")
        plt.xlabel("Document Rank (Sorted by Score)")
        plt.ylabel("Distance Score")
        plt.grid(True)

        # Legend
        legend_labels = [plt.Line2D([0], [0], marker='o', color='w', label=src,
                                    markerfacecolor=color_map[src], markersize=10)
                         for src in color_map]
        plt.legend(handles=legend_labels, title="Source")
        plt.show()



if __name__ == "__main__":
    while True:
        query = input("\n📝 Enter a query (or type 'exit' to quit): ")
        if query.lower() == "exit":
            break
        retrieve_and_plot_with_langraph_query(query)


