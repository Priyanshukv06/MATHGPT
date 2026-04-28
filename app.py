"""
MathGPT v2  ·  app.py
Entry point for the Streamlit application.
"""
import uuid
import streamlit as st

from ui.styles  import inject_styles, render_welcome
from ui.sidebar import render_sidebar
from utils.agent  import build_agent_executor
from utils.latex  import render_response
from utils.supabase_client import save_message, is_enabled as supabase_enabled
from tools.graph_plotter import pending_plot

from langchain_community.callbacks import StreamlitCallbackHandler

# ── Page config (must be first Streamlit call) ────────────────────────────
st.set_page_config(
    page_title = "MathGPT",
    page_icon  = "🧮",
    layout     = "wide",
    initial_sidebar_state = "expanded",
)

inject_styles()

# ── Persistent session id (for Supabase) ──────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

# ── Sidebar ───────────────────────────────────────────────────────────────
cfg = render_sidebar()

if not cfg["api_key"]:
    render_welcome()
    st.stop()

# ── Build (or re-use cached) agent ────────────────────────────────────────
try:
    agent = build_agent_executor(cfg["api_key"], cfg["model"])
except Exception as exc:
    st.error(f"❌ Could not initialise agent: {exc}")
    st.info("Check your Groq API key and try again.")
    st.stop()

# ── Chat history ──────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role"   : "assistant",
            "content": (
                "Hi! I'm **MathGPT** 🧮  \n"
                "I can solve equations, compute integrals, plot graphs, "
                "answer reasoning questions, and search Wikipedia.  \n"
                "What would you like to work on?"
            ),
        }
    ]

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        render_response(msg["content"])

# ── Input ─────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask me anything maths-related…"):
    # Show user message
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        if cfg["show_steps"]:
            cb_container = st.container()
        else:
            cb_container = st.empty()     # hidden — still needed for callbacks

        st_cb = StreamlitCallbackHandler(cb_container, expand_new_thoughts=cfg["show_steps"])

        with st.spinner("Thinking…"):
            try:
                result = agent.invoke(
                    {"input": prompt},
                    config={"callbacks": [st_cb]},
                )
                answer = result.get("output", "Sorry, I couldn't generate a response.")
            except Exception as exc:
                answer = (
                    f"⚠️ **Error:** {exc}  \n\n"
                    "Please rephrase your question or check your API key."
                )

        # Render the final answer
        render_response(answer)

        # Render pending graph (if Graph Plotter tool was triggered)
        if pending_plot["fig"] is not None:
            st.markdown(f"📈 *{pending_plot['label']}*")
            st.pyplot(pending_plot["fig"])
            pending_plot["fig"]   = None
            pending_plot["label"] = ""

    # Persist to session state + Supabase
    st.session_state["messages"].append({"role": "assistant", "content": answer})
    if supabase_enabled():
        sid = st.session_state["session_id"]
        save_message(sid, "user",      prompt, cfg["model"])
        save_message(sid, "assistant", answer, cfg["model"])
