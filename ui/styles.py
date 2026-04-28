import streamlit as st

_CSS = """
<style>
/* ── Hide default Streamlit chrome ───────── */
#MainMenu, footer { visibility: hidden; }

/* ── Chat message polish ─────────────────── */
.stChatMessage { border-radius: 12px; }

/* ── Welcome hero ────────────────────────── */
.hero {
    text-align: center;
    padding: 4rem 2rem;
}
.hero h1 { font-size: 3.5rem; margin-bottom: .5rem; }
.hero p  { font-size: 1.15rem; color: #94a3b8; margin-bottom: .75rem; }

/* ── Feature pill badges ─────────────────── */
.feature-badge {
    display: inline-block;
    background: #1e1b4b;
    border: 1px solid #4c1d95;
    border-radius: 999px;
    padding: .25rem .85rem;
    font-size: .85rem;
    margin: .2rem;
    color: #c4b5fd;
}

/* ── Code blocks in chat ─────────────────── */
.stMarkdown code { font-size: .85rem; }

/* ── Sidebar logo ────────────────────────── */
.sidebar-logo {
    font-size: 1.6rem;
    font-weight: 800;
    letter-spacing: -.5px;
    color: #a78bfa;
}
</style>
"""

_WELCOME_FEATURES = [
    "⚡ SymPy Calculator", "∫ Integral Solver", "📐 Equation Solver",
    "📈 Graph Plotter", "🔍 Wikipedia Search", "🧠 Reasoning Engine",
    "💬 Conversation Memory", "📥 Chat Export",
]

def inject_styles() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def render_welcome() -> None:
    badges = "".join(f'<span class="feature-badge">{f}</span>' for f in _WELCOME_FEATURES)
    st.markdown(
        f"""
        <div class="hero">
            <div style="font-size:4rem">🧮</div>
            <h1>MathGPT</h1>
            <p>AI-powered math assistant — step-by-step solutions, graph plotting & Wikipedia search.</p>
            <p>Powered by <strong>Groq</strong> + <strong>LangChain</strong> + <strong>Streamlit</strong></p>
            <div style="margin-top:1.5rem">{badges}</div>
            <hr style="margin:2rem auto;width:40%;border-color:#334155">
            <p style="font-size:.95rem">
                👈 Enter your <strong>Groq API key</strong> in the sidebar to get started.<br>
                Get a free key at <a href="https://console.groq.com" target="_blank">console.groq.com</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
