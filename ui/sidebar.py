import os
import streamlit as st
from config import (
    PROVIDERS, DEFAULT_PROVIDER,
    NVIDIA_MODELS, GROQ_MODELS,
    DEFAULT_NVIDIA_MODEL, DEFAULT_GROQ_MODEL,
    APP_VERSION, GITHUB_URL,
)
from utils.export import export_as_json, export_as_markdown
from utils.supabase_client import is_enabled, get_all_sessions, load_full_session


def _get_key(name: str) -> str:
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, "")


def _load_session(session_id: str) -> None:
    """Load a previous session into current state and rerun."""
    messages = load_full_session(session_id)
    if messages:
        # Convert DB rows to display format
        st.session_state["messages"] = [
            {"role": m["role"], "content": m["content"]}
            for m in messages
        ]
        # Also reload into LangChain memory
        st.session_state["lc_chat_history"] = []
        for m in messages:
            if m["role"] == "user":
                st.session_state["lc_chat_history"].append(
                    {"type": "human", "content": m["content"]}
                )
            else:
                st.session_state["lc_chat_history"].append(
                    {"type": "ai", "content": m["content"]}
                )
        # Switch to this session's ID so new messages go to same session
        st.session_state["session_id"] = session_id
        st.rerun()


def render_sidebar() -> dict:
    with st.sidebar:
        st.markdown('<p class="sidebar-logo">🧮 MathGPT</p>', unsafe_allow_html=True)
        st.caption(f"v{APP_VERSION}")
        st.divider()

        # ── Provider selector ─────────────────────────────────────────
        provider = st.selectbox(
            "🔌 Provider",
            options=list(PROVIDERS.keys()),
            format_func=lambda k: PROVIDERS[k],
            index=0,   # NVIDIA first
        )

        # ── API Key (auto-load from secrets/env, else show input) ─────
        key_name   = "NVIDIA_API_KEY" if provider == "nvidia" else "GROQ_API_KEY"
        secret_key = _get_key(key_name)

        if secret_key:
            api_key = secret_key
            st.success(f"✅ {key_name} loaded", icon="🔑")
        else:
            placeholder = "nvapi-..." if provider == "nvidia" else "gsk_..."
            help_url    = "build.nvidia.com" if provider == "nvidia" else "console.groq.com"
            api_key = st.text_input(
                f"{PROVIDERS[provider]} API Key",
                type        = "password",
                placeholder = placeholder,
                help        = f"Free key at {help_url}",
            )

        st.divider()

        # ── Model selector ────────────────────────────────────────────
        model_dict    = NVIDIA_MODELS if provider == "nvidia" else GROQ_MODELS
        default_model = DEFAULT_NVIDIA_MODEL if provider == "nvidia" else DEFAULT_GROQ_MODEL

        model = st.selectbox(
            "🤖 Model",
            options      = list(model_dict.keys()),
            format_func  = lambda k: model_dict[k],
            index        = list(model_dict.keys()).index(default_model),
        )

        show_steps = st.toggle("🔍 Show reasoning steps", value=False)
        st.divider()

        # ── Session stats ─────────────────────────────────────────────
        msgs    = st.session_state.get("messages", [])
        q_count = sum(1 for m in msgs if m["role"] == "user")
        if q_count:
            st.markdown("**📊 Session Stats**")
            st.markdown(
                f"- Questions : **{q_count}**\n"
                f"- Messages  : **{len(msgs)}**\n"
                f"- Provider  : `{provider.upper()}`\n"
                f"- Model     : `{model.split('/')[-1][:20]}`"
            )
            if is_enabled():
                st.caption("☁️ Persisting to Supabase")
            st.divider()

        # ── Export ────────────────────────────────────────────────────
        if len(msgs) > 1:
            st.markdown("**📥 Export Chat**")
            c1, c2 = st.columns(2)
            with c1:
                st.download_button("JSON", export_as_json(msgs),
                    "mathgpt_chat.json", "application/json", use_container_width=True)
            with c2:
                st.download_button("MD", export_as_markdown(msgs),
                    "mathgpt_chat.md", "text/markdown", use_container_width=True)
            st.divider()

        # ── Clear ─────────────────────────────────────────────────────
        if st.button("🗑️ Clear chat", use_container_width=True):
            st.session_state["messages"]       = []
            st.session_state["lc_chat_history"] = []
            st.rerun()

        # ── Previous Sessions (ChatGPT-style) ────────────────────────────────
        if is_enabled():
            st.divider()
            st.markdown("**🕘 Previous Sessions**")

            sessions = get_all_sessions()

            if not sessions:
                st.caption("No previous sessions yet.")
            else:
                # Show max 10 recent sessions
                for s in sessions[:10]:
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        # Highlight current session
                        is_current = s["session_id"] == st.session_state.get("session_id", "")
                        label = f"{'📍 ' if is_current else ''}{s['title']}"
                        if st.button(label, key=f"sess_{s['session_id']}", use_container_width=True):
                            if not is_current:
                                _load_session(s["session_id"])
                    with col2:
                        st.caption(s["created_at"])

        st.divider()
        st.markdown(
            f"[📂 Source]({GITHUB_URL})  •  "
            "[🔑 NVIDIA Key](https://build.nvidia.com)  •  "
            "[🔑 Groq Key](https://console.groq.com)",
        )

    return {
        "provider"   : provider,
        "api_key"    : api_key,
        "model"      : model,
        "show_steps" : show_steps,
    }
