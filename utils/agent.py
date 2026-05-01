import os
import streamlit as st
from langchain.agents.agent import AgentExecutor
from langchain.agents.react.agent import create_react_agent
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

from tools.calculator    import calculator_tool
from tools.wiki_search   import wikipedia_tool
from tools.reasoning     import build_reasoning_tools
from tools.graph_plotter import graph_tool
from config import MEMORY_WINDOW, MAX_ITERATIONS, MAX_EXECUTION_TIME, REACT_TEMPLATE


@st.cache_resource(show_spinner=False)
def _get_llm(provider: str, api_key: str, model: str):
    if provider == "nvidia":
        from langchain_nvidia_ai_endpoints import ChatNVIDIA
        return ChatNVIDIA(
            model       = model,
            nvidia_api_key = api_key,
            temperature = 0,
            max_tokens  = 2048,
        )
    else:  # groq
        from langchain_groq import ChatGroq
        return ChatGroq(
            model        = model,
            groq_api_key = api_key,
            temperature  = 0,
            streaming    = True,
        )


def build_agent_executor(provider: str, api_key: str, model: str) -> AgentExecutor:
    llm = _get_llm(provider, api_key, model)

    history = StreamlitChatMessageHistory(key="lc_chat_history")
    memory  = ConversationBufferWindowMemory(
        chat_memory     = history,
        k               = MEMORY_WINDOW,
        memory_key      = "chat_history",
        return_messages = False,
        input_key       = "input",
        output_key      = "output",
    )

    reasoning_tool, integral_tool = build_reasoning_tools(llm)
    tools = [calculator_tool, wikipedia_tool, reasoning_tool, integral_tool, graph_tool]

    prompt = PromptTemplate(
        input_variables = ["tools", "tool_names", "chat_history", "input", "agent_scratchpad"],
        template        = REACT_TEMPLATE,
    )

    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(
        agent                   = agent,
        tools                   = tools,
        memory                  = memory,
        handle_parsing_errors   = True,
        max_iterations          = MAX_ITERATIONS,
        max_execution_time      = MAX_EXECUTION_TIME,
        early_stopping_method   = "generate",
        verbose                 = False,
    )
