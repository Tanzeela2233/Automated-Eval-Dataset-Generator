import streamlit as st
import pandas as pd
from generator import generate_dataset
from evaluator import evaluate_dataset
from document import build_jsonl, build_csv

st.set_page_config(
    page_title="Automated Eval Dataset Generator",
    page_icon="🧪",
    layout="wide",
)

st.markdown("""
<style>
.main-title {font-size: 2.5rem; font-weight: 800; margin-bottom: 0.2rem;}
.subtitle {color: #64748b; font-size: 1.05rem; margin-bottom: 1.5rem;}
.card {padding: 1rem; border-radius: 14px; border: 1px solid #e2e8f0; background: #f8fafc;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🧪 Automated Eval Dataset Generator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Generate high-quality evaluation datasets from a task description using Groq-powered LLM generation and automatic quality checks.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("⚙️ Configuration")
    topic = st.text_input(
        "Task / Domain",
        value="Customer support question answering",
        help="Describe the task your evaluation dataset should test.",
    )
    num_examples = st.slider("Number of examples", 5, 50, 10)
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Mixed"], index=3)
    output_format = st.selectbox("Download format", ["JSONL", "CSV"])
    st.divider()
    st.caption("Powered by Groq API")
    st.caption("Model: openai/gpt-oss-20b")

generate = st.button("🚀 Generate Evaluation Dataset", type="primary", use_container_width=True)

if generate:
    if not topic.strip():
        st.error("Please enter a task or domain.")
        st.stop()

    with st.spinner("Generating evaluation examples with Groq..."):
        try:
            rows = generate_dataset(topic, num_examples, difficulty)
        except Exception as exc:
            st.error(f"Generation failed: {exc}")
            st.stop()

    with st.spinner("Evaluating generated examples..."):
        try:
            evaluated = evaluate_dataset(rows, topic)
        except Exception as exc:
            st.error(f"Evaluation failed: {exc}")
            st.stop()

    st.session_state["dataset"] = evaluated
    st.session_state["topic"] = topic
    st.session_state["format"] = output_format

if "dataset" in st.session_state:
    dataset = st.session_state["dataset"]

    passed = sum(1 for row in dataset if row.get("evaluation", {}).get("passed"))
    total = len(dataset)
    avg_score = (
        sum(float(row.get("evaluation", {}).get("score", 0)) for row in dataset) / total
        if total else 0
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Examples", total)
    c2.metric("Passed", f"{passed}/{total}")
    c3.metric("Average Score", f"{avg_score:.1f}/10")

    st.subheader("📊 Evaluation Overview")
    chart_df = pd.DataFrame(
        {
            "Example": list(range(1, total + 1)),
            "Score": [row["evaluation"]["score"] for row in dataset],
        }
    ).set_index("Example")
    st.bar_chart(chart_df)

    st.subheader("🧾 Generated Dataset")
    display_rows = []
    for i, row in enumerate(dataset, 1):
        ev = row["evaluation"]
        display_rows.append(
            {
                "ID": i,
                "Input": row["input"],
                "Expected Output": row["expected_output"],
                "Score": ev["score"],
                "Passed": "✅" if ev["passed"] else "❌",
                "Reason": ev["reason"],
            }
        )

    st.dataframe(pd.DataFrame(display_rows), use_container_width=True, hide_index=True)

    st.subheader("🔎 Detailed Evaluation")
    for i, row in enumerate(dataset, 1):
        ev = row["evaluation"]
        with st.expander(f"Example {i} — {'PASS' if ev['passed'] else 'REVIEW'} — {ev['score']}/10"):
            st.write("**Input**")
            st.write(row["input"])
            st.write("**Expected output**")
            st.write(row["expected_output"])
            st.write("**Evaluation**")
            st.write(ev["reason"])

    if st.session_state["format"] == "JSONL":
        data_bytes = build_jsonl(dataset)
        file_name = "evaluation_dataset.jsonl"
        mime = "application/json"
    else:
        data_bytes = build_csv(dataset)
        file_name = "evaluation_dataset.csv"
        mime = "text/csv"

    st.download_button(
        "⬇️ Download Evaluation Dataset",
        data=data_bytes,
        file_name=file_name,
        mime=mime,
        use_container_width=True,
    )
else:
    st.info("Configure the dataset in the sidebar, then click **Generate Evaluation Dataset**.")
    st.markdown("""
    ### What this app does
    1. Converts your task description into evaluation examples.
    2. Generates inputs and expected outputs with Groq.
    3. Runs a second LLM-based quality evaluation.
    4. Shows scores, pass/fail results, and reasons.
    5. Exports the final dataset as JSONL or CSV.
    """)
