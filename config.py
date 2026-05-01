# ─────────────────────────────────────────────
#  MathGPT  ·  config.py
# ─────────────────────────────────────────────

APP_TITLE    = "MathGPT"
APP_ICON     = "🧮"
APP_VERSION  = "2.1.0"
GITHUB_URL   = "https://github.com/Priyanshukv06/MATHGPT"

# ── Providers ─────────────────────────────────
PROVIDERS = {
    "nvidia": "🟢 NVIDIA NIM",
    "groq"  : "⚡ Groq",
}
DEFAULT_PROVIDER = "nvidia"   # NVIDIA is now primary

# ── NVIDIA Models (verified IDs from build.nvidia.com April 2026) ──────
NVIDIA_MODELS = {
    "deepseek-ai/deepseek-r1"                    : "🧠 DeepSeek R1 671B (Best Math)",
    "nvidia/llama-3.3-nemotron-super-49b-v1"     : "🔥 Nemotron Super 49B (Agentic)",
    "meta/llama-3.3-70b-instruct"                : "⚡ Llama 3.3 70B (Fast)",
    "meta/llama-3.1-70b-instruct"                : "💡 Llama 3.1 70B",
    "qwen/qwen2.5-72b-instruct"                  : "📐 Qwen 2.5 72B (Reasoning)",
    "mistralai/mistral-small-3.1-24b-instruct"   : "🌀 Mistral Small 24B",
}

# ── Groq Models ───────────────────────────────
GROQ_MODELS = {
    "llama-3.3-70b-versatile" : "⚡ Llama 3.3 70B",
    "gemma2-9b-it"            : "🚀 Gemma 2 9B (Fast)",
    "mixtral-8x7b-32768"      : "🔀 Mixtral 8x7B",
    "llama3-8b-8192"          : "💨 Llama 3 8B (Fastest)",
}

DEFAULT_NVIDIA_MODEL = "nvidia/llama-3.3-nemotron-super-49b-v1"
DEFAULT_GROQ_MODEL   = "llama-3.3-70b-versatile"

MEMORY_WINDOW      = 10
MAX_ITERATIONS     = 15
MAX_EXECUTION_TIME = 60   # seconds timeout

# ── ReAct Prompt ──────────────────────────────
REACT_TEMPLATE = """You are MathGPT, an expert AI assistant specialising in mathematics, \
calculus, algebra, statistics, and logical reasoning.

CRITICAL RULES:
- ALWAYS format mathematical expressions using LaTeX notation.
- Use \\( ... \\) for INLINE math: e.g. \\( \\sin^2(x) + \\cos^2(x) = 1 \\)
- Use \\[ ... \\] for BLOCK/DISPLAY math equations on their own line.
- NEVER write raw math without LaTeX delimiters.
- If you already KNOW the answer from your training (formulas, definitions, theorems), \
answer DIRECTLY without using any tool.
- ONLY use tools when you need to COMPUTE, SOLVE an integral, or PLOT a graph.

TOOLS AVAILABLE (use only when necessary):
{tools}

FORMAT — use EXACTLY:
Question: the input question you must answer
Thought: Do I need a tool? If the answer is in my training knowledge, go to Final Answer directly.
Action: one of [{tool_names}]
Action Input: what you pass to the tool
Observation: the result of the action
Thought: I now know the final answer
Final Answer: the final, complete answer with ALL math in LaTeX format

Previous conversation:
{chat_history}

Question: {input}
Thought:{agent_scratchpad}"""
