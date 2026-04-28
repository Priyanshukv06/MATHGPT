import streamlit as st
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

from tools.calculator   import calculator_tool
from tools.wiki_search  import wikipedia_tool
from tools.reasoning    import build_reasoning_tools
from tools.graph_plotter import graph_tool
from config import MEMORY_WINDOW, MAX_ITERATIONS, REACT_TEMPLATE


@st.cache_resource(show_spinner=False)
def _get_llm(api_key: str, model: str) -> ChatGroq:
    return ChatGroq(
        model=model,
        groq_api_key=api_key,
        temperature=0,
        streaming=True,
    )


def build_agent_executor(api_key: str, model: str) -> AgentExecutor:
    llm = _get_llm(api_key, model)

    # ── Memory backed by Streamlit session_state ──────────────────────
    history = StreamlitChatMessageHistory(key="lc_chat_history")
    memory  = ConversationBufferWindowMemory(
        chat_memory  = history,
        k            = MEMORY_WINDOW,
        memory_key   = "chat_history",
        return_messages = False,   # plain text — matches PromptTemplate
        input_key    = "input",
        output_key   = "output",
    )

    # ── Build tools (reasoning tools need the LLM) ────────────────────
    reasoning_tool, integral_tool = build_reasoning_tools(llm)
    tools = [calculator_tool, wikipedia_tool, reasoning_tool, integral_tool, graph_tool]

    # ── Inline ReAct prompt (no hub dependency) ───────────────────────
    prompt = PromptTemplate(
        input_variables=["tools", "tool_names", "chat_history", "input", "agent_scratchpad"],
        template=REACT_TEMPLATE,
    )

    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(
        agent              = agent,
        tools              = tools,
        memory             = memory,
        handle_parsing_errors = True,
        max_iterations     = MAX_ITERATIONS,
        verbose            = False,
    )
