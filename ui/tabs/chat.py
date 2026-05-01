import streamlit as st
from langchain_community.callbacks import StreamlitCallbackHandler
from utils.latex import render_response
from utils.supabase_client import save_message, is_enabled as supabase_enabled
from tools.graph_plotter import pending_plot

def render_chat_tab(agent, cfg):
    for msg in st.session_state.get("messages", []):
        with st.chat_message(msg["role"]):
            render_response(msg["content"])

    if prompt := st.chat_input("Ask me anything maths-related…"):
        st.session_state.setdefault("messages", []).append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            cb = st.container() if cfg["show_steps"] else st.empty()
            st_cb = StreamlitCallbackHandler(cb, expand_new_thoughts=cfg["show_steps"])
            with st.spinner("Thinking…"):
                try:
                    result = agent.invoke({"input": prompt}, config={"callbacks": [st_cb]})
                    answer = result.get("output", "Sorry, I could not generate a response.")
                except Exception as exc:
                    err = str(exc)
                    if "iteration" in err.lower() or "time" in err.lower():
                        answer = "⚠️ Too many steps. Try asking more specifically."
                    elif "rate" in err.lower() or "429" in err:
                        answer = "⏱️ **Rate limit hit.** Wait 30 s or switch to Groq."
                    else:
                        answer = f"⚠️ **Error:** {exc}"
            render_response(answer)
            if pending_plot["fig"] is not None:
                st.markdown(f"📈 *{pending_plot['label']}*")
                st.pyplot(pending_plot["fig"])
                pending_plot["fig"] = None; pending_plot["label"] = ""
        st.session_state["messages"].append({"role": "assistant", "content": answer})
        if supabase_enabled():
            sid = st.session_state["session_id"]
            save_message(sid, "user", prompt, cfg["model"])
            save_message(sid, "assistant", answer, cfg["model"])