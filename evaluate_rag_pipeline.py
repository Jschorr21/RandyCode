import csv
from deepeval.test_case import LLMTestCase
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    TaskCompletionMetric

)
from datetime import datetime
from deepeval import evaluate as deepeval_evaluate
import re, json

from langchain_pipeline.langraph_pipeline import LangGraphPipeline
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langchain_pipeline.langraph_builder import LangGraphBuilder
from langchain_core.messages import ToolMessage
import uuid
from deepeval.test_case import ToolCall
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
def extract_tools_called(state):
    tools_called = []
    for msg in state["channel_values"]["messages"]:
        if hasattr(msg, "tool_calls"):
            for call in msg.tool_calls:
                if isinstance(call, dict):
                    name = call.get("name")
                    arguments = call.get("args", {})
                    if name:
                        tools_called.append(ToolCall(name=name, arguments=arguments))
    return tools_called

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
                match = re.search(r"\[DOCS_LIST_JSON_START](.*?)\[DOCS_LIST_JSON_END]", m.content, re.DOTALL)
                if match:
                    try:
                        docs = json.loads(match.group(1))
                        retrieved_contexts.extend(docs)
                        continue
                    except Exception as e:
                        print(f"⚠️ Failed to parse docs_list JSON: {e}")

                # fallback
                retrieved_contexts.append(m.content)

        # ✅ No join, just pass the list directly
        context = retrieved_contexts if retrieved_contexts else []
        tools_used = extract_tools_called(state)
        print("TOOOLS CALLED:\n\n")
        print(tools_used)
        print("\n\n")
        llm_test_cases.append(
            LLMTestCase(
                input=query,
                actual_output=actual_output,
                expected_output=expected_output,
                retrieval_context=context,  # ✅ Each doc is a separate string
                context=context,  # (optional)
                tools_called=tools_used   # fallback
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
    correctness_metric = GEval(
    name="Correctness",
    evaluation_steps=[
        "Check whether the facts in 'actual output' contradict any facts in 'expected output'",
        "You should also heavily penalize omission of detail",
        "Vague language, or contradicting OPINIONS, are OK"
    ],
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.EXPECTED_OUTPUT,
    ]
)
    metrics = [
        AnswerRelevancyMetric(model="gpt-4o-mini"),
        FaithfulnessMetric(model="gpt-4o-mini"), 
        ContextualRecallMetric(model="gpt-4o-mini"),
        ContextualRelevancyMetric(model="gpt-4o-mini"),
        TaskCompletionMetric(model="gpt-4o-mini"),
        GEval(
        name="Correctness", 
        evaluation_steps=[
            "Check whether the facts in 'actual output' contradict any facts in 'expected output'",
            "You should also heavily penalize omission of detail",
            "Vague language, or contradicting OPINIONS, are OK"
        ],
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ], model="gpt-4o-mini",
    )
    ]
    

    print("🧪 Running DeepEval...")
    results = deepeval_evaluate(test_cases=llm_test_cases, metrics=metrics, run_async=True)

    print(f"📝 Writing results to {output_txt_path}...")
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(f"RAG Evaluation Results - {datetime.now()}\n\n")
        for i, (test_case, test_result_list) in enumerate(results):
            # f.write(f"Test Case {i + 1}\n")
            # f.write(f"Query: {test_case.input}\n")
            # f.write(f"Expected Output: {test_case.expected_output}\n")
            # f.write(f"Actual Output: {test_case.actual_output}\n")

            # if test_case.context:
            #     f.write(f"Context:\n{test_case.context[0][:1000]}...\n")
            # else:
            #     f.write("Context: None\n")

            # # Ensure test_result_list is actually a list
            if not isinstance(test_result_list, list):
                test_result_list = [test_result_list]
            i=0
            for test_result in test_result_list:
                f.write(f"Test Case {i + 1}\n")
                i+=1
                if hasattr(test_result, "metrics_data"):
                    for metric in test_result.metrics_data:
                        score = metric.score if hasattr(metric, "score") else "N/A"
                        name = metric.name if hasattr(metric, "name") else "Unnamed Metric"
                        reason = metric.reason if hasattr(metric, "reason") else "No reason provided."
                        f.write(f"{name}: {score if isinstance(score, str) else round(score, 2)}\n")
                        f.write(f"Reason: {reason}\n\n")
                else:
                    f.write("⚠️ Invalid test_result object: not a TestResult\n\n")

            f.write("-" * 50 + "\n\n")



    print("✅ Done!")

if __name__ == "__main__":
    evaluate("rag_eval_test_data.csv")