# ─────────────────────────────────────────────
#  MathGPT  ·  config.py
# ─────────────────────────────────────────────

APP_TITLE       = "MathGPT"
APP_ICON        = "🧮"
APP_VERSION     = "2.0.0"
GITHUB_URL      = "https://github.com/Priyanshukv06/MATHGPT"

# ── Models ───────────────────────────────────
AVAILABLE_MODELS: dict[str, str] = {
    "llama-3.3-70b-versatile" : "⚡ Llama 3.3 70B  (Best Quality)",
    "gemma2-9b-it"            : "🚀 Gemma 2 9B     (Fast)",
    "mixtral-8x7b-32768"      : "🔀 Mixtral 8x7B   (Long Context)",
    "llama3-8b-8192"          : "💨 Llama 3 8B     (Fastest)",
}
DEFAULT_MODEL   = "llama-3.3-70b-versatile"
MEMORY_WINDOW   = 10        # turns kept in ConversationBufferWindowMemory
MAX_ITERATIONS  = 8         # agent steps cap

# ── Prompts ───────────────────────────────────
REACT_TEMPLATE = """You are MathGPT, an expert AI assistant specialising in mathematics, \
calculus, algebra, statistics, and logical reasoning. \
You always explain solutions clearly and step-by-step.

TOOLS AVAILABLE:
{tools}

FORMAT — use EXACTLY:
Question: the input question you must answer
Thought: think step-by-step about what to do
Action: one of [{tool_names}]
Action Input: what you pass to the tool
Observation: the result of the action
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now know the final answer
Final Answer: the final, complete answer to the question

Previous conversation:
{chat_history}

Question: {input}
Thought:{agent_scratchpad}"""

REASONING_TEMPLATE = """You are a world-class mathematics and reasoning expert.
Solve the following problem with a clear, step-by-step explanation.
Show ALL working and justify each step.

Question: {question}

Solution:"""

INTEGRAL_TEMPLATE = """You are an expert calculus teacher.
Solve the following integral with COMPLETE, detailed steps.
State the technique used (substitution, by-parts, partial fractions, etc.) and verify the result.

Integral: {function}

Step-by-step solution:"""
