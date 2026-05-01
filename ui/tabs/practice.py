"""
ui/tabs/practice.py  v3  — ALL 3 METHODS INTEGRATED
─────────────────────────────────────────────────────
Method 1 : HuggingFace bulk import (via terminal script)
Method 2 : CSV bulk upload (in-app drag-and-drop UI)
Method 3 : Manual single-question add (in-app form)
─────────────────────────────────────────────────────
Practice solver uses question bank first, AI fallback second.
"""

import re
import streamlit as st
from utils.latex import render_response
from utils.supabase_client import save_practice_attempt, is_enabled as supabase_enabled
from utils.question_bank import (
    add_question, get_random_question, get_all_questions,
    get_questions, delete_question, count_questions,
)

TOPICS = {
    "🔢 Algebra"        : "algebra (equations, inequalities, polynomials, factoring)",
    "📈 Calculus"       : "calculus (derivatives, integrals, limits, differential equations)",
    "📐 Trigonometry"   : "trigonometry (identities, equations, inverse functions)",
    "🎲 Probability"    : "probability and statistics (distributions, combinatorics)",
    "📊 Linear Algebra" : "linear algebra (matrices, determinants, eigenvalues)",
    "🔷 Geometry"       : "geometry and coordinate geometry (areas, volumes, conic sections)",
}

DIFFICULTY_DESC = {
    "Easy"  : "straightforward single-step, suitable for a high school student",
    "Medium": "multi-step, requires clear working, suitable for a first-year university student",
    "Hard"  : "challenging, requires deep understanding, suitable for an advanced student",
}

VALID_TOPICS = list(TOPICS.keys())
VALID_DIFFS  = ["Easy", "Medium", "Hard"]


def _build_llm(cfg: dict):
    """Safe LLM builder that works regardless of provider."""
    provider = cfg.get("provider", "groq").lower()
    api_key  = cfg.get("api_key", "")
    model    = cfg.get("model", "")

    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model           = model,
            groq_api_key    = api_key,
            temperature     = 0,
            streaming       = False,
        )
    else:
        from langchain_nvidia_ai_endpoints import ChatNVIDIA
        import os
        os.environ["NVIDIA_API_KEY"] = api_key
        return ChatNVIDIA(model=model, temperature=0)


def _generate_ai_problem(llm, topic: str, difficulty: str, subtopic: str) -> str:
    from langchain.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    tmpl = PromptTemplate(
        input_variables=["topic", "difficulty_desc", "subtopic"],
        template=(
            "Generate ONE original mathematics practice problem on {topic}.\\n"
            "Difficulty: {difficulty_desc}.\\n"
            "{subtopic}\\n"
            "RULES:\\n"
            "- Write the problem statement ONLY — no solution, no hints.\\n"
            "- Use LaTeX notation for all math: \\\\( ... \\\\) for inline, \\\\[ ... \\\\] for block.\\n"
            "- End with exactly: Show your working.\\n\\n"
            "Problem:"
        ),
    )
    chain = tmpl | llm | StrOutputParser()
    return chain.invoke({
        "topic"          : topic,
        "difficulty_desc": DIFFICULTY_DESC[difficulty],
        "subtopic"       : f"Focus on: {subtopic}." if subtopic.strip() else "",
    })


def _evaluate_answer(llm, problem: str, solution: str, user_answer: str) -> tuple:
    """Evaluate user answer. Uses stored solution if available, otherwise LLM judges."""
    from langchain.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    if solution.strip():
        solution_context = f"Reference Solution (use this to evaluate):\\n{solution}"
    else:
        solution_context = "No reference solution provided — use your own mathematical knowledge."

    tmpl = PromptTemplate(
        input_variables=["problem", "solution_context", "user_answer"],
        template=(
            "You are evaluating a student\\'s math answer.\\n\\n"
            "Problem:\\n{problem}\\n\\n"
            "{solution_context}\\n\\n"
            "Student\\'s Answer:\\n{user_answer}\\n\\n"
            "Provide:\\n"
            "1. ✅ Correct / ❌ Incorrect / ⚠️ Partially correct\\n"
            "2. Complete step-by-step correct solution (LaTeX for all math)\\n"
            "3. What the student did well\\n"
            "4. What needs improvement\\n\\n"
            "End your response with EXACTLY this line:\\n"
            "SCORE: X/10"
        ),
    )
    chain  = tmpl | llm | StrOutputParser()
    feedback = chain.invoke({
        "problem"          : problem,
        "solution_context" : solution_context,
        "user_answer"      : user_answer,
    })
    m = re.search(r"SCORE:\\s*(\\d+)/10", feedback)
    score = int(m.group(1)) if m else 5
    return feedback, score


# ── Admin panel ───────────────────────────────────────────────────────

def _render_admin_panel() -> None:
    st.markdown("### 🗃️ Question Bank Admin")
    st.markdown("Add your own real-world questions. Practice mode will use these first before generating AI questions.")

    add_tab, view_tab = st.tabs(["➕ Add Question", "📋 View / Delete"])

    with add_tab:
        with st.form("add_question_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                q_topic = st.selectbox("Topic", list(TOPICS.keys()), key="aq_topic")
            with c2:
                q_diff  = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], key="aq_diff")

            q_source   = st.text_input("Source (optional)", placeholder="e.g. NCERT Ex 5.3 Q7, JEE 2023, MIT OCW")
            q_tags     = st.text_input("Tags (optional)",   placeholder="e.g. integration, definite, substitution")
            q_question = st.text_area(
                "Question *",
                placeholder="Write the full question here. Use LaTeX: \\\\( x^2 \\\\) for inline, \\\\[ \\\\int_0^1 x\\\\,dx \\\\] for block.",
                height=140,
            )
            q_solution = st.text_area(
                "Solution / Answer Key *",
                placeholder="Write the complete step-by-step solution here. This is used for accurate evaluation.",
                height=140,
            )

            submitted = st.form_submit_button("✅ Add to Bank", type="primary", use_container_width=True)
            if submitted:
                if not q_question.strip() or not q_solution.strip():
                    st.error("Question and Solution are required.")
                else:
                    ok = add_question(
                        topic      = q_topic,
                        difficulty = q_diff,
                        question   = q_question,
                        solution   = q_solution,
                        source     = q_source,
                        tags       = q_tags,
                    )
                    if ok:
                        st.success(f"✅ Added to bank! ({q_topic} · {q_diff})")
                    else:
                        st.error("Failed to save. Check your setup.")

    with view_tab:
        f1, f2 = st.columns(2)
        with f1: filter_topic = st.selectbox("Filter by topic",      ["All"] + list(TOPICS.keys()), key="vq_topic")
        with f2: filter_diff  = st.selectbox("Filter by difficulty", ["All", "Easy", "Medium", "Hard"], key="vq_diff")

        topic_arg = "" if filter_topic == "All" else filter_topic
        diff_arg  = "" if filter_diff  == "All" else filter_diff
        questions = get_all_questions() if (not topic_arg and not diff_arg) else []
        if topic_arg or diff_arg:
            from utils.question_bank import get_questions
            questions = get_questions(topic_arg, diff_arg)

        if not questions:
            st.info("No questions in the bank yet. Add some using the ➕ tab!")
        else:
            st.caption(f"Showing **{len(questions)}** question(s)")
            for q in questions:
                with st.expander(f"[{q.get('difficulty','?')}] {q.get('topic','?')} — {q.get('question','')[:60]}…"):
                    st.markdown(f"**Topic:** {q.get('topic','—')}  |  **Difficulty:** {q.get('difficulty','—')}")
                    if q.get("source"):
                        st.markdown(f"**Source:** {q.get('source')}")
                    if q.get("tags"):
                        st.markdown(f"**Tags:** `{q.get('tags')}`")
                    st.markdown("**Question:**")
                    render_response(q.get("question", ""))
                    with st.expander("👁️ Show Solution"):
                        render_response(q.get("solution", ""))
                    if q.get("id"):
                        if st.button(f"🗑️ Delete", key=f"del_{q['id']}"):
                            delete_question(q["id"])
                            st.success("Deleted!")
                            st.rerun()


# ── Main practice tab ─────────────────────────────────────────────────

def render_practice_tab(agent, cfg: dict) -> None:
    st.markdown("## 🧪 Practice Mode")

    # ── Tabs: Practice | Admin ─────────────────────────────────────────
    practice_view, admin_view = st.tabs(["🎯 Solve Problems", "🗃️ Manage Question Bank"])

    with admin_view:
        _render_admin_panel()

    with practice_view:
        _render_practice_solver(cfg)


def _render_practice_solver(cfg: dict) -> None:
    # Session state init
    for key, default in [
        ("practice_score",   0),
        ("practice_total",   0),
        ("practice_streak",  0),
        ("current_problem",  None),
        ("current_solution", ""),
        ("current_source",   ""),
        ("show_feedback",    False),
        ("last_feedback",    ""),
        ("last_score",       0),
        ("from_bank",        False),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # ── Stats bar ──────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    total = st.session_state["practice_total"]
    score = st.session_state["practice_score"]
    acc   = (score / (total * 10) * 100) if total else 0
    with c1: st.metric("🏆 Score",          f"{score}/{total*10}" if total else "0/0")
    with c2: st.metric("📝 Problems Done",   total)
    with c3: st.metric("🔥 Streak",          st.session_state["practice_streak"])
    with c4: st.metric("🎯 Accuracy",        f"{acc:.0f}%")

    if total > 0:
        st.progress(acc / 100)

    st.divider()

    # ── Settings ───────────────────────────────────────────────────────
    s1, s2, s3 = st.columns([2, 1, 2])
    with s1: topic_label = st.selectbox("📚 Topic",      list(TOPICS.keys()))
    with s2: difficulty  = st.selectbox("⚡ Difficulty", ["Easy", "Medium", "Hard"])
    with s3: subtopic    = st.text_input("🎯 Subtopic (optional)", placeholder="e.g. integration by parts")

    topic = TOPICS[topic_label]

    # Bank count indicator
    bank_count = count_questions(topic_label, difficulty)
    if bank_count > 0:
        st.success(f"✅ **{bank_count} question(s)** in your bank for {topic_label} · {difficulty} — will use these first!")
    else:
        st.info(f"ℹ️ No bank questions for {topic_label} · {difficulty} — AI will generate one. Add real questions in the **🗃️ Manage Question Bank** tab!")

    g1, g2 = st.columns([1, 3])
    with g1:
        generate = st.button("🎲 New Problem", type="primary", use_container_width=True)
    with g2:
        if st.button("🗑️ Reset Score", use_container_width=True):
            for k in ["practice_score", "practice_total", "practice_streak"]:
                st.session_state[k] = 0
            st.rerun()

    if generate:
        # ── Try question bank first ────────────────────────────────────
        bank_q = get_random_question(topic_label, difficulty)

        if bank_q:
            st.session_state["current_problem"]  = bank_q["question"]
            st.session_state["current_solution"] = bank_q.get("solution", "")
            st.session_state["current_source"]   = bank_q.get("source", "")
            st.session_state["from_bank"]        = True
        else:
            # ── Fall back to AI generation ─────────────────────────────
            with st.spinner("Generating problem with AI…"):
                try:
                    llm = _build_llm(cfg)
                    problem = _generate_ai_problem(llm, topic, difficulty, subtopic)
                    st.session_state["current_problem"]  = problem
                    st.session_state["current_solution"] = ""
                    st.session_state["current_source"]   = "AI Generated"
                    st.session_state["from_bank"]        = False
                except Exception as e:
                    st.error(f"Failed to generate problem: {e}")
                    return

        st.session_state["show_feedback"] = False
        st.rerun()

    # ── Problem display ────────────────────────────────────────────────
    if not st.session_state["current_problem"]:
        st.info("👆 Click **New Problem** to get started!")
        return

    source_badge = (
        f"📚 `{st.session_state['current_source']}`"
        if st.session_state["current_source"]
        else "🤖 `AI Generated`"
    )
    bank_badge = "🗃️ From Your Bank" if st.session_state["from_bank"] else "🤖 AI Generated"

    st.markdown(f"### 📋 Problem · `{difficulty}` · {topic_label} · {bank_badge}")
    if st.session_state.get("current_source"):
        st.caption(f"Source: {st.session_state['current_source']}")
    render_response(st.session_state["current_problem"])
    st.divider()

    # ── Answer input ───────────────────────────────────────────────────
    if not st.session_state["show_feedback"]:
        user_answer = st.text_area(
            "✏️ Your Solution",
            placeholder=(
                "Write your complete working here.\\n"
                "LaTeX tip: use \\\\( x^2 \\\\) for inline math, \\\\[ \\\\int x\\\\,dx \\\\] for block."
            ),
            height=160,
        )

        if st.button("✅ Submit Answer", type="primary") and user_answer.strip():
            with st.spinner("Evaluating…"):
                try:
                    llm = _build_llm(cfg)
                    feedback, fb_score = _evaluate_answer(
                        llm,
                        st.session_state["current_problem"],
                        st.session_state["current_solution"],
                        user_answer,
                    )
                except Exception as e:
                    st.error(f"Evaluation error: {e}")
                    return

            st.session_state["show_feedback"]   = True
            st.session_state["last_feedback"]   = feedback
            st.session_state["last_score"]      = fb_score
            st.session_state["practice_score"] += fb_score
            st.session_state["practice_total"] += 1
            st.session_state["practice_streak"] = (
                st.session_state["practice_streak"] + 1 if fb_score >= 7 else 0
            )

            if supabase_enabled():
                save_practice_attempt(
                    session_id  = st.session_state.get("session_id", "unknown"),
                    topic       = topic_label,
                    difficulty  = difficulty,
                    question    = st.session_state["current_problem"],
                    user_answer = user_answer,
                    score       = fb_score,
                )
            st.rerun()

    else:
        # ── Feedback display ───────────────────────────────────────────
        fb_score = st.session_state["last_score"]
        if   fb_score >= 8: st.success(f"🎉 Excellent! **{fb_score}/10**")
        elif fb_score >= 6: st.info(   f"👍 Good effort! **{fb_score}/10**")
        else:               st.warning(f"📚 Keep practicing! **{fb_score}/10**")

        st.markdown("### 📝 Feedback & Full Solution")
        render_response(st.session_state["last_feedback"])

        if st.button("➡️ Next Problem", type="primary"):
            st.session_state["current_problem"]  = None
            st.session_state["current_solution"] = ""
            st.session_state["current_source"]   = ""
            st.session_state["show_feedback"]    = False
            st.rerun()