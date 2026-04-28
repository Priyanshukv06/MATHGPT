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
| 📥 **Chat Export** | Download your session as **JSON** or **Markdown** |
| ☁️ **Supabase Persistence** | Optional cross-session chat history saved to PostgreSQL |
| 🤖 **Multi-Model** | Switch between Llama 3.3 70B, Gemma 2 9B, Mixtral 8x7B in the sidebar |

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
# Edit .env and add your GROQ_API_KEY
```

> 🔑 Get a free Groq key at [console.groq.com](https://console.groq.com)

### 3 · Run

```bash
streamlit run app.py
```

App opens at **http://localhost:8501** 🎉

---

## ☁️ Deploy to Streamlit Community Cloud

1. **Push** this repo to your GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select `Priyanshukv06/MATHGPT`, branch `main`, file `app.py`
4. Under **Advanced settings → Secrets**, add:

```toml
# Required
GROQ_API_KEY = "gsk_your_key_here"

# Optional — Supabase persistence
SUPABASE_URL = "https://xxxx.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

5. Click **Deploy** — live in ~2 minutes ✅

---

## ⏱️ Keep-Alive (Cron Job)

Streamlit Community Cloud sleeps after 24h of inactivity.  
This repo ships a **GitHub Actions workflow** that pings your app every 12 hours — no external service needed.

**Setup:**
1. Copy your deployed app URL
2. Go to **GitHub → Settings → Secrets → Actions**
3. Add secret: `STREAMLIT_APP_URL` = `https://your-app.streamlit.app`
4. The workflow at `.github/workflows/keep_alive.yml` handles the rest

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
│
├── tools/
│   ├── calculator.py             # SymPy-powered math solver
│   ├── wiki_search.py            # Wikipedia API wrapper
│   ├── reasoning.py              # LCEL reasoning + integral chains
│   └── graph_plotter.py          # matplotlib function grapher
│
├── utils/
│   ├── agent.py                  # AgentExecutor + memory builder
│   ├── latex.py                  # LaTeX detection & rendering
│   ├── export.py                 # JSON + Markdown export
│   └── supabase_client.py        # Optional persistence layer
│
├── ui/
│   ├── sidebar.py                # Model picker, stats, export buttons
│   └── styles.py                 # Custom CSS + welcome screen
│
├── .streamlit/
│   └── config.toml               # Dark theme
│
├── .github/
│   └── workflows/
│       └── keep_alive.yml        # Cron ping every 12h
│
├── requirements.txt
├── .env.example
└── .gitignore
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
