import csv
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric
)
from datetime import datetime
from deepeval import evaluate as deepeval_evaluate

from langchain_pipeline.langraph_pipeline import LangGraphPipeline
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langchain_pipeline.langraph_builder import LangGraphBuilder
from langchain_core.messages import ToolMessage
import uuid
def load_test_data_from_csv(filepath):
    test_cases = []
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        if 'query' not in reader.fieldnames:
            raise ValueError(f"CSV is missing required 'query' column. Found columns: {reader.fieldnames}")
        for row in reader:
            test_cases.append({
                "query": row["query"],
                "expected_output": row.get("expected_output", "")
            })
    return test_cases
def run_stateless_graph(query):
    llm = ChatOpenAI(model="gpt-4o")
    builder = LangGraphBuilder(llm)
    graph = builder.build_graph()
    thread_id = f"thread_{uuid.uuid4()}"
    memory = builder.memory

    response = graph.invoke(
        {"messages": [{"role": "user", "content": query}]},
        config={"configurable": {"thread_id": thread_id}}
    )

    state = memory.get({"configurable": {"thread_id": thread_id}})
    return response["messages"][-1].content, state
# 2. Run RAG assistant and collect context + output
def run_and_collect_metrics(test_cases):
    llm_test_cases = []

    for test in test_cases:
        query = test["query"]
        expected_output = test.get("expected_output", "")
        print(f"🔍 Running query: {query}")

        actual_output, state = run_stateless_graph(query)

        retrieved_contexts = []
        for m in state["channel_values"]["messages"]:
            if isinstance(m, ToolMessage) and m.content.strip():
                print("📦 ToolMessage.additional_kwargs:")
                print(m.additional_kwargs)
                artifact = m.additional_kwargs.get("artifact", {})
                docs_list = artifact.get("docs_list")

                if isinstance(docs_list, list):
                    retrieved_contexts.extend(docs_list)
                else:
                    # fallback to content if docs_list isn't available
                    retrieved_contexts.append(m.content)

        # ✅ No join, just pass the list directly
        context = retrieved_contexts if retrieved_contexts else []

        llm_test_cases.append(
            LLMTestCase(
                input=query,
                actual_output=actual_output,
                expected_output=expected_output,
                retrieval_context=context,  # ✅ Each doc is a separate string
                context=context  # (optional)
            )
        )
    print(f"✅ {len(context)} documents added to context for: {query}")
    # print(f"retrieved context 1:\n\n{context[0]}\n\n")
    print(f"retrieved context 2:\n\n{context[1]}\n\n")
    print(f"retrieved context 3:\n\n{context[2]}\n\n")
    return llm_test_cases

# 3. Evaluate and write to .txt file
def evaluate(csv_file_path, output_txt_path="rag_eval_results.txt"):
    test_cases = load_test_data_from_csv(csv_file_path)
    llm_test_cases = run_and_collect_metrics(test_cases)

    # metrics = [
    #     AnswerRelevancyMetric(),
    #     FaithfulnessMetric()
    # ]

    # print("🧪 Running DeepEval...")
    # results = deepeval_evaluate(test_cases=llm_test_cases, metrics=metrics)

    # print(f"📝 Writing results to {output_txt_path}...")
    # with open(output_txt_path, "w", encoding="utf-8") as f:
    #     f.write(f"RAG Evaluation Results - {datetime.now()}\n\n")
    #     for i, (test_case, test_result_list) in enumerate(results):
    #         f.write(f"Test Case {i + 1}\n")
    #         # f.write(f"Query: {test_case.input}\n")
    #         # f.write(f"Expected Output: {test_case.expected_output}\n")
    #         # f.write(f"Actual Output: {test_case.actual_output}\n")

    #         # if test_case.context:
    #         #     f.write(f"Context:\n{test_case.context[0][:1000]}...\n")
    #         # else:
    #         #     f.write("Context: None\n")

    #         # # Ensure test_result_list is actually a list
    #         if not isinstance(test_result_list, list):
    #             test_result_list = [test_result_list]

    #         for test_result in test_result_list:
    #             if hasattr(test_result, "metrics_data"):
    #                 for metric in test_result.metrics_data:
    #                     score = metric.score if hasattr(metric, "score") else "N/A"
    #                     name = metric.name if hasattr(metric, "name") else "Unnamed Metric"
    #                     reason = metric.reason if hasattr(metric, "reason") else "No reason provided."
    #                     f.write(f"{name}: {score if isinstance(score, str) else round(score, 2)}\n")
    #                     f.write(f"Reason: {reason}\n\n")
    #             else:
    #                 f.write("⚠️ Invalid test_result object: not a TestResult\n\n")

    #         f.write("-" * 50 + "\n\n")



    # print("✅ Done!")

if __name__ == "__main__":
    evaluate("evaluate_rag_pipeline_2.csv")