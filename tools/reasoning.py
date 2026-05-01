from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import Tool

# These chains are built lazily so we don't need LLM at import time
_reasoning_chain = None
_integral_chain   = None

REASONING_PROMPT = PromptTemplate(
    input_variables=["question"],
    template=(
        "You are a world-class mathematics and reasoning expert.\n"
        "Solve the following problem with a clear, step-by-step explanation.\n"
        "Show ALL working and justify each step.\n\n"
        "Question: {question}\n\nSolution:"
    ),
)

INTEGRAL_PROMPT = PromptTemplate(
    input_variables=["function"],
    template=(
        "You are an expert calculus teacher.\n"
        "Solve the following integral with COMPLETE, detailed steps.\n"
        "State the technique used (substitution, integration by parts, etc.) "
        "and verify the result.\n\n"
        "Integral: {function}\n\nStep-by-step solution:"
    ),
)

def _get_chains(llm):
    global _reasoning_chain, _integral_chain
    if _reasoning_chain is None:
        _reasoning_chain = REASONING_PROMPT | llm | StrOutputParser()
        _integral_chain  = INTEGRAL_PROMPT  | llm | StrOutputParser()
    return _reasoning_chain, _integral_chain

def build_reasoning_tools(llm):
    rc, ic = _get_chains(llm)

    reasoning_tool = Tool(
        name="Reasoning Tool",
        func=lambda q: rc.invoke({"question": q}),
        description=(
            "Solves logical, word problems, and mathematical reasoning questions "
            "with step-by-step explanations. "
            "Input: the full question or problem statement."
        ),
    )

    integral_tool = Tool(
        name="Integral Solver",
        func=lambda f: ic.invoke({"function": f}),
        description=(
            "Solves definite or indefinite integrals with complete working steps. "
            "Input examples: 'sin(x)', 'x^2 * e^x from 0 to 1', '1/(x^2+1)'. "
        ),
    )
    return reasoning_tool, integral_tool
