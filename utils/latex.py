"""utils/latex.py — Convert all LaTeX notation to Streamlit-compatible format."""
import re
import streamlit as st


def _convert(text: str) -> str:
    # \\[ ... \\]  →  block $$
    text = re.sub(
        r'\\\\\[\s*([\s\S]+?)\s*\\\\\]',
        lambda m: f'\n$$\n{m.group(1).strip()}\n$$\n',
        text
    )
    # \[ ... \]  →  block $$
    text = re.sub(
        r'\\\[\s*([\s\S]+?)\s*\\\]',
        lambda m: f'\n$$\n{m.group(1).strip()}\n$$\n',
        text,
        flags=re.DOTALL
    )
    # \\( ... \\)  →  inline $
    text = re.sub(
        r'\\\\\(\s*([\s\S]+?)\s*\\\\\)',
        lambda m: f'${m.group(1).strip()}$',
        text
    )
    # \( ... \)  →  inline $
    text = re.sub(
        r'\\\(\s*([\s\S]+?)\s*\\\)',
        lambda m: f'${m.group(1).strip()}$',
        text
    )
    return text


def render_response(text: str) -> None:
    if not text:
        return
    converted  = _convert(text)
    block_pat  = re.compile(r'\$\$([\s\S]+?)\$\$', flags=re.DOTALL)
    parts      = block_pat.split(converted)

    if len(parts) == 1:
        st.markdown(converted)
        return

    for i, part in enumerate(parts):
        if not part.strip():
            continue
        if i % 2 == 1:
            try:
                st.latex(part.strip())
            except Exception:
                st.markdown(f"$${part.strip()}$$")
        else:
            st.markdown(part)