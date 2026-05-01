import re
import math
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application,
)
from langchain_core.tools import Tool

_TRANSFORMS = standard_transformations + (implicit_multiplication_application,)

def solve_math(expression: str) -> str:
    """Solve a mathematical expression or equation using SymPy."""
    expr_clean = expression.strip()
    try:
        # Equation solving  (e.g. "x^2 - 5x + 6 = 0")
        if "=" in expr_clean and "==" not in expr_clean:
            lhs_str, rhs_str = expr_clean.split("=", 1)
            lhs = parse_expr(lhs_str.strip(), transformations=_TRANSFORMS)
            rhs = parse_expr(rhs_str.strip(), transformations=_TRANSFORMS)
            solutions = sp.solve(lhs - rhs)
            if solutions:
                return f"Solutions: {solutions}"
            return "No real solutions found."

        expr  = parse_expr(expr_clean, transformations=_TRANSFORMS)
        simp  = sp.simplify(expr)
        if simp.is_number:
            approx = float(simp.evalf())
            return f"Result: {simp}  ≈  {approx:.8g}"
        return f"Simplified: {simp}"

    except Exception as sym_err:
        # numeric fallback — safe eval
        try:
            allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
            result = eval(expr_clean, {"__builtins__": {}}, allowed)   # noqa: S307
            return f"Result: {result}"
        except Exception:
            return f"Could not evaluate '{expression}'. Error: {sym_err}"


calculator_tool = Tool(
    name="Calculator",
    func=solve_math,
    description=(
        "Solves arithmetic, algebraic expressions, and equations symbolically. "
        "Input examples: '2+3*5', 'x^2 - 5x + 6 = 0', 'sin(pi/4)', 'sqrt(144)'. "
        "Use this for any numeric or symbolic computation."
    ),
)
