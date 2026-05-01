import streamlit as st
from utils.latex import render_response
from utils.supabase_client import save_message, is_enabled as supabase_enabled


def _extract_pdf_text(uploaded_file) -> tuple:
    try:
        import fitz
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages_text = []
        for i, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                pages_text.append(f"--- Page {i+1} ---\n{text.strip()}")
        return "\n\n".join(pages_text), len(doc)
    except ImportError:
        st.error("PyMuPDF not installed. Run: pip install PyMuPDF")
        return "", 0
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return "", 0


def _run_pdf_query(agent, cfg: dict, question: str, pdf_text: str, label: str = "") -> None:
    full_prompt = (
        f"You are analyzing content from a PDF document. "
        f"Use the provided PDF content to answer.\n\n"
        f"PDF Content:\n{pdf_text[:4500]}\n\n"
        f"Task: {question}\n\n"
        f"Provide a complete, step-by-step answer. Use LaTeX for all math expressions."
    )
    if label:
        st.markdown(f"**{label}**")
    with st.spinner("Analyzing PDF and solving…"):
        try:
            result = agent.invoke({"input": full_prompt})
            answer = result.get("output", "Could not process.")
        except Exception as e:
            answer = f"⚠️ Error: {e}"

    st.markdown("### 📝 Solution")
    render_response(answer)

    if supabase_enabled() and "session_id" in st.session_state:
        fname = st.session_state.get("pdf_filename", "unknown.pdf")
        save_message(st.session_state["session_id"], "user",
                     f"[PDF: {fname}] {question}", cfg["model"])
        save_message(st.session_state["session_id"], "assistant", answer, cfg["model"])


def render_pdf_tab(agent, cfg: dict) -> None:
    st.markdown("## 📄 PDF Math Solver")
    st.markdown(
        "Upload a math textbook page, exam paper, or worksheet — "
        "then ask questions, auto-solve problems, or generate practice questions."
    )

    uploaded = st.file_uploader(
        "Drop your PDF here",
        type=["pdf"],
        help="Max 10 MB. Works best with text-based PDFs (not scanned images).",
    )

    if uploaded is None:
        st.info("👆 Upload a PDF to get started")
        return

    with st.spinner(f"Reading *{uploaded.name}*…"):
        text, num_pages = _extract_pdf_text(uploaded)

    if not text:
        st.error("Could not extract text. Make sure it is a text-based PDF, not a scanned image.")
        return

    st.success(f"✅ Extracted text from **{num_pages} pages** ({len(text):,} characters)")
    st.session_state["pdf_text"]     = text
    st.session_state["pdf_filename"] = uploaded.name

    with st.expander("📃 Preview extracted text"):
        st.text_area(
            "Content",
            value=text[:3000] + ("…" if len(text) > 3000 else ""),
            height=200,
            disabled=True,
        )

    st.divider()

    action = st.radio(
        "What do you want to do with this PDF?",
        [
            "❓ Ask a question",
            "🔍 Extract & solve all problems",
            "📝 Summarize key formulas",
            "🧪 Generate practice questions",
        ],
        horizontal=True,
    )

    if action == "❓ Ask a question":
        question = st.text_input("Your question:", placeholder="e.g. Solve question 3 on page 2")
        if st.button("🔍 Answer", type="primary") and question:
            _run_pdf_query(agent, cfg, question, text, label=f"**Your question:** {question}")

    elif action == "🔍 Extract & solve all problems":
        if st.button("⚡ Extract & Solve All", type="primary"):
            q = (
                "Identify ALL mathematical problems/questions in this PDF and solve "
                "each one step-by-step. Number them clearly."
            )
            _run_pdf_query(agent, cfg, q, text)

    elif action == "📝 Summarize key formulas":
        if st.button("📝 Extract Formulas", type="primary"):
            q = (
                "Extract and list ALL mathematical formulas, identities, and theorems "
                "from this PDF. Format each in LaTeX notation with a brief label."
            )
            _run_pdf_query(agent, cfg, q, text)

    elif action == "🧪 Generate practice questions":
        c1, c2 = st.columns(2)
        with c1:
            difficulty = st.select_slider("Difficulty", ["Easy", "Medium", "Hard"], value="Medium")
        with c2:
            count = st.slider("Number of questions", 3, 10, 5)
        if st.button("🎲 Generate Questions", type="primary"):
            q = (
                f"Based on the mathematics in this PDF, generate {count} original "
                f"{difficulty.lower()} practice questions similar to the content style. "
                f"For each: show the question, then the complete solution below it."
            )
            _run_pdf_query(agent, cfg, q, text)