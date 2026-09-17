# 🧪 Automated Eval Dataset Generator

> Generate, evaluate, visualize, and export AI evaluation datasets using **Streamlit + Groq**.

[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Groq](https://img.shields.io/badge/LLM-Groq-f55036)](https://groq.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)

## ✨ Overview

**Automated Eval Dataset Generator** is a Streamlit application that creates structured evaluation datasets for AI systems.

You provide a task or domain, choose the number of examples and difficulty, and the application:

1. Generates evaluation examples with an LLM.
2. Creates an expected output for each example.
3. Automatically evaluates dataset quality with a second LLM pass.
4. Calculates scores and pass/fail results.
5. Visualizes evaluation scores.
6. Exports the dataset as **JSONL** or **CSV**.

## 🏗️ Architecture

```text
                 ┌──────────────────────────┐
                 │       Streamlit UI       │
                 │          app.py          │
                 └────────────┬─────────────┘
                              │
                ┌─────────────▼─────────────┐
                │       generator.py        │
                │   Generate eval examples  │
                └─────────────┬─────────────┘
                              │
                       ┌──────▼──────┐
                       │  Groq LLM   │
                       │ GPT-OSS 20B │
                       └──────┬──────┘
                              │
                ┌─────────────▼─────────────┐
                │       evaluator.py       │
                │ Quality / score / pass   │
                └─────────────┬─────────────┘
                              │
                ┌─────────────▼─────────────┐
                │       document.py         │
                │       JSONL / CSV         │
                └───────────────────────────┘
```

## 🚀 Features

- 🤖 LLM-powered evaluation dataset generation
- 🧪 Automatic dataset quality evaluation
- 📊 Interactive score visualization
- ✅ Pass/fail quality checks
- 📄 JSONL export
- 📊 CSV export
- 🔐 Secure Groq API key handling through Streamlit Secrets
- ☁️ Streamlit Community Cloud ready
- 🧩 Modular Python architecture

## 📁 Project Structure

```text
automated-eval-dataset-generator/
│
├── app.py
├── generator.py
├── evaluator.py
├── document.py
├── prompts.py
├── requirements.txt
└── README.md
```

## 🧠 Model

The project uses:

```text
openai/gpt-oss-20b
```

The model is accessed through the Groq API.

> Model availability and pricing/rate limits can change. Check the current Groq model documentation before deployment.

## 🔑 1. Get a Groq API Key

Create a Groq API key from the Groq console.

Never put the API key directly inside Python source code.

## 💻 2. Run Locally

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/automated-eval-dataset-generator.git
cd automated-eval-dataset-generator
```

Create a virtual environment:

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Set the API key.

### PowerShell

```powershell
$env:GROQ_API_KEY="your_groq_api_key"
```

Run:

```bash
streamlit run app.py
```

## ☁️ 3. Deploy to Streamlit Community Cloud

Push the complete project to GitHub.

Then:

1. Open Streamlit Community Cloud.
2. Connect your GitHub account.
3. Click **Create app**.
4. Select your repository.
5. Select the `main` branch.
6. Set the main file to:

```text
app.py
```

7. Open **Advanced settings**.
8. Add the following secret:

```toml
GROQ_API_KEY = "your_groq_api_key"
```

9. Deploy.

Do **not** commit your real API key to GitHub.

## 🔐 Secrets

For local development, you can also create:

```text
.streamlit/
└── secrets.toml
```

with:

```toml
GROQ_API_KEY = "your_groq_api_key"
```

Add this to `.gitignore`:

```text
.streamlit/secrets.toml
__pycache__/
*.pyc
venv/
.env
```

## 📊 Evaluation Logic

Every generated example receives:

- **Score:** 0–10
- **Passed:** `true` when score is at least 7
- **Reason:** explanation of the quality assessment

The evaluator checks:

| Criterion | Purpose |
|---|---|
| Relevance | Does the example test the requested task? |
| Clarity | Is the example understandable? |
| Correctness | Is the expected output appropriate? |
| Usefulness | Is it useful for evaluating an AI system? |
| Ambiguity | Could the example have multiple unclear interpretations? |

## 📦 Output Example

### JSONL

```json
{"input":"Explain what a refund policy means.","expected_output":"A refund policy explains when and how a customer can receive money back.","evaluation":{"score":9,"passed":true,"reason":"Clear and relevant evaluation example."}}
```

### CSV

```text
input,expected_output,score,passed,reason
"Explain what a refund policy means.","A refund policy explains when and how a customer can receive money back.",9,True,"Clear and relevant evaluation example."
```

## 🛠️ Tech Stack

- Python
- Streamlit
- Groq API
- GPT-OSS 20B
- Pandas
- JSON
- CSV
- GitHub
- Streamlit Community Cloud

## 🔮 Future Improvements

Possible production upgrades:

- [ ] Upload an existing dataset
- [ ] Multiple evaluation metrics
- [ ] LLM-as-a-judge comparison
- [ ] Reference-answer similarity scoring
- [ ] Duplicate detection
- [ ] Dataset versioning
- [ ] Batch generation
- [ ] Custom system prompts
- [ ] Multiple Groq model selection
- [ ] Human review workflow
- [ ] Dataset statistics dashboard
- [ ] Hugging Face dataset export

## 📜 License

This project is available for educational and portfolio use.

---

### ⭐ Built with Python, Streamlit, and Groq
