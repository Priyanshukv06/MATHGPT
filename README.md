<div align="center">

# 🧮 MathGPT

**AI-powered math assistant with step-by-step solutions, graph plotting, and Wikipedia search**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.2%2B-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)](https://langchain.com)
[![Groq](https://img.shields.io/badge/Groq-LLM-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com)
[![Supabase](https://img.shields.io/badge/Supabase-Optional-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

[🚀 Live Demo](https://your-app.streamlit.app) · [🐛 Report Bug](https://github.com/Priyanshukv06/MATHGPT/issues) · [✨ Request Feature](https://github.com/Priyanshukv06/MATHGPT/issues)

</div>

---

## ✨ Features

### Core Capabilities
| Feature | Description |
|---|---|
| ⚡ **SymPy Calculator** | Solves arithmetic, algebra, and symbolic math — not just numeric eval |
| ∫ **Integral Solver** | Step-by-step integration with technique explanation (by-parts, substitution…) |
| 📐 **Equation Solver** | Handles linear, quadratic, and higher-degree equations (`x^2 - 5x + 6 = 0`) |
| 📈 **Graph Plotter** | Plot any `y = f(x)` — just ask *"plot y = x² + sin(x) from -5 to 5"* |
| 🔍 **Wikipedia Search** | Fetch definitions, theorems, and mathematical history in context |
| 🧠 **Reasoning Engine** | Logical & word problems with full chain-of-thought explanations |
| 💬 **Conversation Memory** | Remembers last 10 exchanges — ask follow-up questions naturally |
| 📊 **LaTeX Rendering** | Math output auto-detected and rendered with `st.latex()` |

### Practice Mode 🧪
| Feature | Description |
|---|---|
| 📚 **Question Bank** | **19,893 pre-loaded questions** across 6+ topics (Algebra, Calculus, Geometry, etc.) |
| 🤖 **AI Problem Generation** | Generate unlimited problems with configurable difficulty & subtopic |
| ⭐ **Smart Evaluation** | LLM evaluates your answer, gives feedback, shows correct solution |
| 📊 **Scoring & Streaks** | Track accuracy, see progress per topic, build learning streaks |
| 📥 **Import Methods** | Load from HuggingFace (12.5K competition math), CSV, or manual entry |
| 🎯 **Difficulty Levels** | Easy, Medium, Hard — practice adaptive learning |

### Advanced Features
| Feature | Description |
|---|---|
| 📥 **Chat Export** | Download your session as **JSON** or **Markdown** |
| ☁️ **Supabase Persistence** | Optional cross-session chat history saved to PostgreSQL |
| 🤖 **Multi-Model LLM** | **10 models** from NVIDIA (DeepSeek R1, Nemotron 49B, Llama 3.3) & Groq (Gemma, Mixtral) |
| 🔄 **Provider Switching** | Switch between NVIDIA NIM (primary) & Groq (fallback) in sidebar |
| 🌐 **Cloud Ready** | Deploy on Streamlit Cloud with 1 click (GitHub + secrets)

---

## 🏗️ Architecture

```
User Input (st.chat_input)
        │
        ▼
  AgentExecutor  ─── ConversationBufferWindowMemory (k=10)
  (ReAct pattern)        │
        │                └── StreamlitChatMessageHistory
        ▼
  ┌─────────────────────────────────────────────────────┐
  │                     Tool Router                     │
  ├──────────────┬─────────────┬──────────┬────────────┤
  │  Calculator  │   Integral  │Wikipedia │  Reasoning │
  │   (SymPy)    │   Solver    │  Search  │   Engine   │
  └──────────────┴─────────────┴──────────┴────────────┘
        │                                    Graph Plotter
        ▼                                    (matplotlib)
  LaTeX Renderer  →  st.latex() / st.markdown()
        │
        ▼
  Supabase (optional)  →  Persistent chat_history table
```

---

## 🚀 Quick Start

### 1 · Clone & install

```bash
git clone https://github.com/Priyanshukv06/MATHGPT.git
cd MATHGPT
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2 · Configure environment

```bash
cp .env.example .env
# Edit .env and add your API keys:
# NVIDIA_API_KEY=your_nvidia_key_from_build.nvidia.com
# GROQ_API_KEY=your_groq_key_from_console.groq.com
```

> 🔑 **Get API Keys:**
> - **NVIDIA**: [build.nvidia.com](https://build.nvidia.com) (free, 24-hour tokens)
> - **Groq**: [console.groq.com](https://console.groq.com) (free, no rate limits)

### 3 · Load question bank (optional)

The app ships with **19,893 questions** pre-loaded. To add more:

```bash
# Import from HuggingFace (133k questions from 3 datasets)
python scripts/import_huggingface.py --dataset all

# Or import custom CSV
python scripts/bulk_import_csv.py --file your_questions.csv
```

### 4 · Run locally

```bash
streamlit run app.py
```

App opens at **http://localhost:8501** 🎉

---

## ☁️ Deploy to Streamlit Community Cloud

**See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for detailed instructions.**

### Quick Deploy (3 steps)

1. **Prepare repo**
   ```bash
   git add .
   git commit -m "Deploy MathGPT v2.1.0"
   git push origin main
   ```

2. **Create app on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click **New app** → GitHub authentication
   - Select repo → branch `main` → file `app.py`

3. **Add secrets**
   - Go to app settings → **Advanced settings → Secrets**
   - Paste (replace with your actual keys):
   ```toml
   NVIDIA_API_KEY = "your_nvidia_key"
   GROQ_API_KEY = "your_groq_key"
   ```

4. **Deploy** — live in ~2 minutes ✅

### Keep-Alive (Prevent Sleeping)

Streamlit Cloud sleeps after 24h inactivity. Enable auto-pings:

1. Go to GitHub → **Settings → Secrets → Actions**
2. Add: `STREAMLIT_APP_URL` = `https://mathgpt-YOUR-USERNAME.streamlit.app`
3. The workflow at `.github/workflows/keep_alive.yml` auto-runs every 12h

---

## 🗄️ Supabase Setup (Optional)

Run this SQL once in your **Supabase SQL Editor**:

```sql
CREATE TABLE IF NOT EXISTS chat_history (
  id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id TEXT        NOT NULL,
  role       TEXT        NOT NULL CHECK (role IN ('user', 'assistant')),
  content    TEXT        NOT NULL,
  model      TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_history(session_id);
```

When `SUPABASE_URL` and `SUPABASE_KEY` are present in secrets/env, the app automatically persists every conversation. Without them, it falls back silently to in-session memory — no errors.

---

## 📁 Project Structure

```
MATHGPT/
├── app.py                        # Main entry (~90 lines)
├── config.py                     # Models, prompts, constants
├── question_bank.json            # ✅ 19,893 pre-loaded questions
│
├── tools/                        # Math tools (SymPy, graphs, etc.)
│   ├── calculator.py             # SymPy solver (arithmetic, algebra, equations)
│   ├── integral_solver.py        # Integration with technique explanation
│   ├── graph_plotter.py          # matplotlib function grapher
│   ├── reasoning.py              # LCEL reasoning chains
│   └── wiki_search.py            # Wikipedia API wrapper
│
├── utils/                        # Core utilities
│   ├── agent.py                  # LangChain ReAct AgentExecutor
│   ├── latex.py                  # LaTeX → Streamlit conversion pipeline
│   ├── export.py                 # JSON + Markdown chat export
│   ├── question_bank.py          # CRUD for 19.8K questions
│   ├── supabase_client.py        # Optional Supabase persistence
│   └── __init__.py
│
├── ui/                           # Streamlit UI components
│   ├── sidebar.py                # Model selector, API keys, export buttons
│   ├── styles.py                 # Dark theme, welcome screen
│   └── tabs/
│       ├── chat.py               # 💬 Main conversation tab
│       ├── practice.py           # 🧪 AI problem generation + evaluation
│       ├── pdf_solver.py         # 📄 PDF extraction & solving
│       ├── formulas.py           # 📚 Math reference library
│       ├── analytics.py          # 📊 Session stats & progress
│       └── __init__.py
│
├── scripts/                      # Data import tools
│   ├── import_huggingface.py     # ← Import from HuggingFace (133k questions)
│   ├── bulk_import_csv.py        # ← CSV question import with validation
│   └── __init__.py
│
├── data/
│   └── questions_template.csv    # Sample 14 questions (template)
│
├── .streamlit/
│   ├── config.toml               # Dark theme, headless mode
│   └── secrets.toml.example      # Template for cloud secrets
│
├── .github/
│   └── workflows/
│       └── keep_alive.yml        # Auto-ping every 12h (prevent sleep)
│
├── README.md                     # This file
├── DEPLOYMENT_CHECKLIST.md       # Full deployment guide
├── requirements.txt              # All Python dependencies (15 packages)
├── .env.example                  # Template for API keys
└── .gitignore                    # Git security exclusions
```

---

## 💬 Example Queries

```
"Solve x³ - 6x² + 11x - 6 = 0"
"Find the integral of x² * e^x"
"Plot y = sin(x) / x from -20 to 20"
"What is the Fundamental Theorem of Calculus?"
"If a train travels 120 km in 1.5 hours, what is its speed in m/s?"
"Prove that √2 is irrational"
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM Inference** | [Groq](https://groq.com) (llama-3.3-70b, gemma2-9b, mixtral-8x7b) |
| **Agent Framework** | [LangChain](https://langchain.com) v0.2 — `create_react_agent` + `AgentExecutor` |
| **Memory** | `ConversationBufferWindowMemory` + `StreamlitChatMessageHistory` |
| **Symbolic Math** | [SymPy](https://sympy.org) |
| **Graphing** | [Matplotlib](https://matplotlib.org) + NumPy |
| **Frontend** | [Streamlit](https://streamlit.io) 1.35+ |
| **Persistence** | [Supabase](https://supabase.com) PostgreSQL (optional) |
| **CI / Keep-Alive** | GitHub Actions |

---

## 🤝 Contributing

Contributions are welcome!

```bash
# Fork → clone → create branch
git checkout -b feature/your-feature-name

# Make changes, then
git commit -m "feat: your feature description"
git push origin feature/your-feature-name
# Open a Pull Request
```

---

## 📄 License

MIT © [Priyanshukv06](https://github.com/Priyanshukv06)

---

<div align="center">
  <sub>Built with ❤️ using Groq · LangChain · Streamlit</sub>
</div>
