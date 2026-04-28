"""
Render a response string in Streamlit with proper LaTeX support.

Handles:
  $$...$$       — block LaTeX  → st.latex()
  \\[...\\]     — block LaTeX  → st.latex()
  $...$         — inline LaTeX — left inside markdown (Streamlit renders it)
  plain text    — st.markdown()
"""
import re
import streamlit as st

# Patterns that need st.latex() extraction
_BLOCK_SPLIT = re.compile(
    r"(\$\$[\s\S]+?\$\$|\\\[[\s\S]+?\\\])",
    flags=re.DOTALL,
)


def render_response(text: str) -> None:
    if not text:
        return

    if not _BLOCK_SPLIT.search(text):
        # No block LaTeX — render as markdown (handles inline $...$ too)
        st.markdown(text)
        return

    for chunk in _BLOCK_SPLIT.split(text):
        if not chunk.strip():
            continue
        if chunk.startswith("$$") and chunk.endswith("$$"):
            st.latex(chunk[2:-2].strip())
        elif chunk.startswith("\\[") and chunk.endswith("\\]"):
            st.latex(chunk[2:-2].strip())
        else:
            st.markdown(chunk)
