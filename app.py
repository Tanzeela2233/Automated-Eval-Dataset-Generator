
import streamlit as st
import pandas as pd

from generator import generate_dataset
from evaluator import evaluate_dataset
from document import build_jsonl, build_csv


# =========================================================
# Page configuration
# =========================================================

st.set_page_config(
    page_title="Automated Eval Dataset Generator",
    page_icon="🧪",
    layout="wide",
)


# =========================================================
# Custom styling
# =========================================================

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #64748b;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }

    .card {
        padding: 1rem;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        background: #f8fafc;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Header
# =========================================================

st.markdown(
    '<div class="main-title">🧪 Automated Eval Dataset Generator</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
    Generate evaluation datasets from a task description using
    Groq-powered LLM generation and automatic quality checks.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Sidebar
# =========================================================

with st.sidebar:
    st.header("⚙️ Configuration")

    topic = st.text_input(
        "Task / Domain",
        value="Customer support question answering",
        help="Describe the task your evaluation dataset should test.",
    )

    num_examples = st.slider(
        "Number of examples",
        min_value=5,
        max_value=50,
        value=10,
    )

    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard", "Mixed"],
        index=3,
    )

    output_format = st.selectbox(
        "Download format",
        ["JSONL", "CSV"],
    )

    st.divider()

    st.caption("Powered by Groq API")
    st.caption("Model: openai/gpt-oss-20b")


# =========================================================
# Generate button
# =========================================================

generate = st.button(
    "🚀 Generate Evaluation Dataset",
    type="primary",
    use_container_width=True,
)


# =========================================================
# Dataset generation
# =========================================================

if generate:

    if not topic.strip():
        st.error("Please enter a task or domain.")
        st.stop()

    # -----------------------------------------
    # Step 1: Generate examples
    # -----------------------------------------

    with st.spinner("Generating evaluation examples with Groq..."):

        try:
            rows = generate_dataset(
                topic=topic,
                num_examples=num_examples,
                difficulty=difficulty,
            )

        except Exception as exc:
            st.error(f"Generation failed: {exc}")
            st.stop()

    # Check generated data
    if not rows:
        st.error("No evaluation examples were generated.")
        st.stop()

    # -----------------------------------------
    # Step 2: Evaluate examples
    # -----------------------------------------

    with st.spinner("Evaluating generated examples..."):

        try:
            evaluated = evaluate_dataset(
                rows=rows,
                topic=topic,
            )

        except Exception as exc:
            st.error(f"Evaluation failed: {exc}")
            st.stop()

    if not evaluated:
        st.error("Evaluation returned no results.")
        st.stop()

    # -----------------------------------------
    # Save to session state
    # -----------------------------------------

    st.session_state["dataset"] = evaluated
    st.session_state["topic"] = topic
    st.session_state["format"] = output_format


# =========================================================
# Display dataset
# =========================================================

if "dataset" in st.session_state:

    dataset = st.session_state["dataset"]

    total = len(dataset)

    # -----------------------------------------
    # Calculate metrics
    # -----------------------------------------

    passed = sum(
        1
        for row in dataset
        if row.get("evaluation", {}).get("passed", False)
    )

    scores = [
        float(row.get("evaluation", {}).get("score", 0))
        for row in dataset
    ]

    avg_score = sum(scores) / total if total else 0


    # =====================================================
    # Metrics
    # =====================================================

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Examples",
        total,
    )

    c2.metric(
        "Passed",
        f"{passed}/{total}",
    )

    c3.metric(
        "Average Score",
        f"{avg_score:.1f}/10",
    )


    # =====================================================
    # Evaluation chart
    # =====================================================

    st.subheader("📊 Evaluation Overview")

    chart_df = pd.DataFrame(
        {
            "Example": list(range(1, total + 1)),
            "Score": scores,
        }
    )

    chart_df = chart_df.set_index("Example")

    st.bar_chart(chart_df)


    # =====================================================
    # Dataset table
    # =====================================================

    st.subheader("🧾 Generated Dataset")

    display_rows = []

    for i, row in enumerate(dataset, start=1):

        evaluation = row.get("evaluation", {})

        display_rows.append(
            {
                "ID": i,
                "Input": row.get("input", ""),
                "Expected Output": row.get(
                    "expected_output",
                    "",
                ),
                "Score": evaluation.get(
                    "score",
                    0,
                ),
                "Passed": (
                    "✅"
                    if evaluation.get("passed", False)
                    else "❌"
                ),
                "Reason": evaluation.get(
                    "reason",
                    "",
                ),
            }
        )

    display_df = pd.DataFrame(display_rows)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )


    # =====================================================
    # Detailed evaluation
    # =====================================================

    st.subheader("🔎 Detailed Evaluation")

    for i, row in enumerate(dataset, start=1):

        evaluation = row.get(
            "evaluation",
            {},
        )

        score = evaluation.get(
            "score",
            0,
        )

        passed_status = evaluation.get(
            "passed",
            False,
        )

        status = "PASS" if passed_status else "REVIEW"

        with st.expander(
            f"Example {i} — {status} — {score}/10"
        ):

            st.write("**Input**")

            st.write(
                row.get(
                    "input",
                    "",
                )
            )

            st.write("**Expected output**")

            st.write(
                row.get(
                    "expected_output",
                    "",
                )
            )

            st.write("**Evaluation**")

            st.write(
                evaluation.get(
                    "reason",
                    "No evaluation reason provided.",
                )
            )


    # =====================================================
    # Download dataset
    # =====================================================

    st.subheader("📥 Download")

    selected_format = st.session_state.get(
        "format",
        "JSONL",
    )

    if selected_format == "JSONL":

        data_bytes = build_jsonl(dataset)

        file_name = "evaluation_dataset.jsonl"

        mime = "application/json"

    else:

        data_bytes = build_csv(dataset)

        file_name = "evaluation_dataset.csv"

        mime = "text/csv"


    st.download_button(
        label="⬇️ Download Evaluation Dataset",
        data=data_bytes,
        file_name=file_name,
        mime=mime,
        use_container_width=True,
    )


# =========================================================
# Initial screen
# =========================================================

else:

    st.info(
        "Configure the dataset in the sidebar, "
        "then click **Generate Evaluation Dataset**."
    )

    st.markdown(
        """
        ### What this app does

        1. 📝 Takes a task/domain description.
        2. 🤖 Generates evaluation examples using Groq.
        3. 🔍 Automatically evaluates each generated example.
        4. 📊 Calculates scores and pass/fail results.
        5. 📥 Exports the dataset as JSONL or CSV.
        """
    )

