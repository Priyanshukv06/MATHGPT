import uuid
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="MathGPT", page_icon="🧮", layout="wide", initial_sidebar_state="expanded")

from ui.sidebar          import render_sidebar
from ui.tabs.chat        import render_chat_tab
from ui.tabs.pdf_solver  import render_pdf_tab
from ui.tabs.practice    import render_practice_tab
from ui.tabs.formulas    import render_formula_tab
from ui.tabs.analytics   import render_analytics_tab
from utils.agent         import build_agent_executor

if "session_id" not in st.session_state: st.session_state["session_id"] = str(uuid.uuid4())
if "messages"   not in st.session_state: st.session_state["messages"]   = []

cfg = render_sidebar()

if not cfg["api_key"]:
    st.warning(f"⚠️ Add your **{cfg['provider']} API key** in the sidebar to get started.")
    st.stop()

@st.cache_resource(show_spinner="Loading model…")
def get_agent(provider, api_key, model):
    return build_agent_executor(provider, api_key, model)

agent = get_agent(cfg["provider"], cfg["api_key"], cfg["model"])

hdr, btn = st.columns([9, 1])
with hdr: st.markdown("# 🧮 MathGPT")
with btn:
    if st.button("✏️ New", use_container_width=True):
        st.session_state["messages"] = []
        st.session_state["lc_chat_history"] = []
        st.session_state["session_id"] = str(uuid.uuid4())
        st.rerun()

t1, t2, t3, t4, t5 = st.tabs(["💬 Chat","📄 PDF Solver","🧪 Practice","📚 Formulas","📊 Analytics"])
with t1: render_chat_tab(agent, cfg)
with t2: render_pdf_tab(agent, cfg)
with t3: render_practice_tab(agent, cfg)
with t4: render_formula_tab()
with t5: render_analytics_tab()