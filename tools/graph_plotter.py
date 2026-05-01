"""
Graph Plotter Tool
------------------
LangChain tools must return a string.  We store the generated
matplotlib figure in a module-level dict; app.py picks it up
after the agent returns and calls st.pyplot().
"""
import re
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application,
)
import matplotlib
matplotlib.use("Agg")          # headless — no GUI window
import matplotlib.pyplot as plt
from langchain_core.tools import Tool

_TRANSFORMS = standard_transformations + (implicit_multiplication_application,)

# Shared store — app.py reads and clears this after each response
pending_plot: dict = {"fig": None, "label": ""}


def _parse_request(request: str):
    """Return (func_str, x_min, x_max) from free-text like
    'y = x**2 + sin(x), x from -5 to 5'."""
    m = re.search(r"x\s+from\s+(-?\d+\.?\d*)\s+to\s+(-?\d+\.?\d*)", request, re.I)
    x_min, x_max = (-10.0, 10.0)
    if m:
        x_min, x_max = float(m.group(1)), float(m.group(2))

    func_str = re.sub(r",?\s*x\s+from.*", "", request, flags=re.I)
    func_str = re.sub(r"^(y\s*=\s*|f\(x\)\s*=\s*)", "", func_str, flags=re.I).strip()
    return func_str, x_min, x_max


def plot_function(request: str) -> str:
    """Create a matplotlib figure and stash it for Streamlit to render."""
    try:
        func_str, x_min, x_max = _parse_request(request)

        x_sym = sp.Symbol("x")
        expr  = parse_expr(func_str, transformations=_TRANSFORMS, local_dict={"x": x_sym})
        f_np  = sp.lambdify(x_sym, expr, modules=["numpy"])

        xs = np.linspace(x_min, x_max, 1200)
        ys = np.asarray(f_np(xs), dtype=float)
        ys = np.where(np.isfinite(ys), ys, np.nan)

        fig, ax = plt.subplots(figsize=(9, 5))
        fig.patch.set_facecolor("#0F0F0F")
        ax.set_facecolor("#1A1A2E")

        ax.plot(xs, ys, color="#7C3AED", linewidth=2.5, label=f"y = {func_str}")
        ax.axhline(0, color="#555", linewidth=0.8, linestyle="--")
        ax.axvline(0, color="#555", linewidth=0.8, linestyle="--")
        ax.set_xlabel("x", color="#E2E8F0")
        ax.set_ylabel("y", color="#E2E8F0")
        ax.set_title(f"y = {func_str}", color="#E2E8F0", fontsize=13, fontweight="bold")
        ax.tick_params(colors="#E2E8F0")
        ax.legend(facecolor="#1A1A2E", labelcolor="#E2E8F0")
        ax.grid(True, alpha=0.25, color="#444")
        for spine in ax.spines.values():
            spine.set_edgecolor("#444")
        plt.tight_layout()

        pending_plot["fig"]   = fig
        pending_plot["label"] = f"y = {func_str}  |  x ∈ [{x_min}, {x_max}]"
        plt.close(fig)

        return (
            f"Graph generated for y = {func_str} over x ∈ [{x_min}, {x_max}]. "
            "The chart will appear below the response. [GRAPH_READY]"
        )

    except Exception as exc:
        return f"Could not plot '{request}'. Error: {exc}"


graph_tool = Tool(
    name="Graph Plotter",
    func=plot_function,
    description=(
        "Plots a mathematical function as a graph. "
        "Input examples: 'y = x**2 + sin(x)', 'x**3 - 2*x, x from -3 to 3'. "
        "Use ** for exponentiation. Returns confirmation; chart renders automatically."
    ),
)
