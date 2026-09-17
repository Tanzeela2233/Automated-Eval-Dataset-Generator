
import streamlit as st
import pandas as pd

from generator import generate_dataset
from evaluator import evaluate_dataset
from document import build_jsonl, build_csv


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Automated Eval Dataset Generator",
    page_icon="🧪",
    layout="wide",
)


# ============================================================
# CUSTOM CSS
# ============================================================

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

    .metric-card {
        padding: 1rem;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        background: #f8fafc;
    }

    .score-label {
        font-weight: 600;
        margin-bottom: 0.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🧪 Automated Eval Dataset Generator</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Generate high-quality evaluation datasets from a task description "
    "using Groq-powered LLM generation and automatic quality checks."
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR CONFIGURATION
# ============================================================

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

    st.divider()

    generate = st.button(
        "🚀 Generate Evaluation Dataset",
        type="primary",
        use_container_width=True,
    )


# ============================================================
# DATASET GENERATION
# ============================================================

if generate:

    if not topic.strip():
        st.error("Please enter a task or domain.")
        st.stop()

    # --------------------------------------------------------
    # Generate dataset
    # --------------------------------------------------------

    with st.spinner("Generating evaluation examples with Groq..."):

        try:
            rows = generate_dataset(
                topic,
                num_examples,
                difficulty,
            )

        except Exception as exc:
            st.error(f"Generation failed: {exc}")
            st.stop()

    # --------------------------------------------------------
    # Evaluate dataset
    # --------------------------------------------------------

    with st.spinner("Evaluating generated examples..."):

        try:
            evaluated = evaluate_dataset(
                rows,
                topic,
            )

        except Exception as exc:
            st.error(f"Evaluation failed: {exc}")
            st.stop()

    # --------------------------------------------------------
    # Store in session state
    # --------------------------------------------------------

    st.session_state["dataset"] = evaluated
    st.session_state["topic"] = topic
    st.session_state["format"] = output_format


# ============================================================
# DISPLAY RESULTS
# ============================================================

if "dataset" in st.session_state:

    dataset = st.session_state["dataset"]

    # --------------------------------------------------------
    # Calculate statistics
    # --------------------------------------------------------

    total = len(dataset)

    passed = sum(
        1
        for row in dataset
        if row.get("evaluation", {}).get("passed")
    )

    scores = [
        float(row.get("evaluation", {}).get("score", 0))
        for row in dataset
    ]

    avg_score = (
        sum(scores) / total
        if total
        else 0
    )

    pass_rate = (
        (passed / total) * 100
        if total
        else 0
    )


    # ========================================================
    # METRICS
    # ========================================================

    st.subheader("📈 Dataset Summary")

    c1, c2, c3, c4 = st.columns(4)

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

    c4.metric(
        "Pass Rate",
        f"{pass_rate:.0f}%",
    )


    # ========================================================
    # EVALUATION OVERVIEW
    # ========================================================

    st.subheader("📊 Evaluation Overview")

    st.write("Individual evaluation scores:")

    # --------------------------------------------------------
    # Safe chart replacement
    #
    # We intentionally do NOT use st.bar_chart().
    # This avoids the Altair compatibility issue on
    # Streamlit Cloud / Python 3.14.
    # --------------------------------------------------------

    for i, score in enumerate(scores, 1):

        col1, col2 = st.columns([1, 8])

        with col1:
            st.markdown(
                f"**Example {i}**"
            )

        with col2:

            progress_value = max(
                0.0,
                min(
                    1.0,
                    score / 10,
                ),
            )

            st.progress(
                progress_value,
                text=f"Score: {score:.0f}/10",
            )


    # --------------------------------------------------------
    # Score distribution summary
    # --------------------------------------------------------

    st.write("")

    score_df = pd.DataFrame(
        {
            "Score": scores
        }
    )

    score_counts = (
        score_df["Score"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    score_counts.columns = [
        "Score",
        "Number of Examples",
    ]

    st.write("**Score Distribution**")

    st.dataframe(
        score_counts,
        use_container_width=True,
        hide_index=True,
    )


    # ========================================================
    # GENERATED DATASET
    # ========================================================

    st.subheader("🧾 Generated Dataset")

    display_rows = []

    for i, row in enumerate(dataset, 1):

        evaluation = row["evaluation"]

        display_rows.append(
            {
                "ID": i,
                "Input": row["input"],
                "Expected Output": row["expected_output"],
                "Score": evaluation["score"],
                "Passed": (
                    "✅"
                    if evaluation["passed"]
                    else "❌"
                ),
                "Reason": evaluation["reason"],
            }
        )

    display_df = pd.DataFrame(display_rows)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )


    # ========================================================
    # DETAILED EVALUATION
    # ========================================================

    st.subheader("🔎 Detailed Evaluation")

    for i, row in enumerate(dataset, 1):

        evaluation = row["evaluation"]

        status = (
            "PASS"
            if evaluation["passed"]
            else "REVIEW"
        )

        with st.expander(
            f"Example {i} — {status} — "
            f"{evaluation['score']}/10"
        ):

            st.markdown("### 📝 Input")

            st.write(
                row["input"]
            )

            st.markdown("### 🎯 Expected Output")

            st.write(
                row["expected_output"]
            )

            st.markdown("### 🧪 Evaluation")

            st.write(
                evaluation["reason"]
            )


    # ========================================================
    # DOWNLOAD DATASET
    # ========================================================

    st.subheader("📥 Download Dataset")

    if st.session_state["format"] == "JSONL":

        data_bytes = build_jsonl(
            dataset
        )

        file_name = (
            "evaluation_dataset.jsonl"
        )

        mime = "application/json"

    else:

        data_bytes = build_csv(
            dataset
        )

        file_name = (
            "evaluation_dataset.csv"
        )

        mime = "text/csv"


    st.download_button(
        label="⬇️ Download Evaluation Dataset",
        data=data_bytes,
        file_name=file_name,
        mime=mime,
        use_container_width=True,
    )


    # ========================================================
    # DATASET INFORMATION
    # ========================================================

    st.divider()

    st.subheader("ℹ️ Dataset Information")

    info_col1, info_col2 = st.columns(2)

    with info_col1:

        st.markdown(
            f"""
            **Task / Domain:**  
            {st.session_state["topic"]}

            **Difficulty:**  
            {difficulty}

            **Examples Generated:**  
            {total}
            """
        )

    with info_col2:

        st.markdown(
            f"""
            **Passed:**  
            {passed}

            **Pass Rate:**  
            {pass_rate:.0f}%

            **Average Score:**  
            {avg_score:.1f}/10
            """
        )


# ============================================================
# INITIAL STATE
# ============================================================

else:

    st.info(
        "Configure the dataset in the sidebar, "
        "then click **Generate Evaluation Dataset**."
    )

    st.markdown(
        """
        ### 🚀 What this app does

        1. Converts your task description into evaluation examples.
        2. Generates inputs and expected outputs with Groq.
        3. Runs a second LLM-based quality evaluation.
        4. Assigns quality scores and pass/fail results.
        5. Displays evaluation statistics.
        6. Provides detailed evaluation explanations.
        7. Exports the final dataset as JSONL or CSV.

        ### 🧠 Example

        **Task / Domain:**

        `Python programming question answering`

        **Difficulty:**

        `Hard`

        **Examples:**

        `10`

        Click **Generate Evaluation Dataset** to create your evaluation dataset.
        """
    )

