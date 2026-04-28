import streamlit as st
from config import AVAILABLE_MODELS, APP_VERSION, GITHUB_URL
from utils.export import export_as_json, export_as_markdown
from utils.supabase_client import is_enabled


def render_sidebar() -> dict:
    with st.sidebar:
        st.markdown('<p class="sidebar-logo">🧮 MathGPT</p>', unsafe_allow_html=True)
        st.caption(f"v{APP_VERSION}")
        st.divider()

        # ── API Key ───────────────────────────────────────────────────
        # Use st.secrets GROQ_API_KEY if available (Streamlit Cloud),
        # otherwise ask the user.
        try:
            secret_key = st.secrets.get("GROQ_API_KEY", "")
        except (FileNotFoundError, KeyError, Exception):
            secret_key = ""
        if secret_key:
            api_key = secret_key
            st.success("✅ API Key loaded from secrets", icon="🔑")
        else:
            api_key = st.text_input(
                "Groq API Key",
                type="password",
                placeholder="gsk_...",
                help="Free key at console.groq.com",
            )

        st.divider()

        # ── Model selector ────────────────────────────────────────────
        model = st.selectbox(
            "🤖 Model",
            options=list(AVAILABLE_MODELS.keys()),
            format_func=lambda k: AVAILABLE_MODELS[k],
            index=0,
        )

        # ── Reasoning steps toggle ────────────────────────────────────
        show_steps = st.toggle("🔍 Show reasoning steps", value=False)

        st.divider()

        # ── Session stats ─────────────────────────────────────────────
        msgs = st.session_state.get("messages", [])
        q_count = sum(1 for m in msgs if m["role"] == "user")
        if q_count:
            st.markdown("**📊 Session Stats**")
            st.markdown(
                f"- Questions: **{q_count}**\n"
                f"- Messages : **{len(msgs)}**\n"
                f"- Model    : `{model.split('-')[0]}`"
            )
            if is_enabled():
                st.caption("☁️ Persisting to Supabase")
            st.divider()

        # ── Export chat ───────────────────────────────────────────────
        if len(msgs) > 1:
            st.markdown("**📥 Export Chat**")
            c1, c2 = st.columns(2)
            with c1:
                st.download_button(
                    "JSON", export_as_json(msgs),
                    "mathgpt_chat.json", "application/json",
                    use_container_width=True,
                )
            with c2:
                st.download_button(
                    "MD", export_as_markdown(msgs),
                    "mathgpt_chat.md", "text/markdown",
                    use_container_width=True,
                )
            st.divider()

        # ── Clear ─────────────────────────────────────────────────────
        if st.button("🗑️ Clear chat", use_container_width=True):
            st.session_state["messages"]      = []
            st.session_state["lc_chat_history"] = []
            st.rerun()

        st.divider()
        st.markdown(
            f"[📂 Source]({GITHUB_URL})  •  "
            "[🔑 Get Groq Key](https://console.groq.com)",
            unsafe_allow_html=True,
        )

    return {"api_key": api_key, "model": model, "show_steps": show_steps}
