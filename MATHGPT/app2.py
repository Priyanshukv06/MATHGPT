import streamlit as st
from langchain_groq import ChatGroq
from langchain.chains import LLMMathChain, LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.agents.agent_types import AgentType
from langchain.agents import Tool, initialize_agent
from langchain.callbacks import StreamlitCallbackHandler
import re

# Set up the Streamlit app
st.set_page_config(page_title="Math Problem Solver & Knowledge Assistant", page_icon="🔢")
st.title("Text-to-Math Problem Solver Using Google Gemma 2")

# Get Groq API Key
groq_api_key = st.sidebar.text_input(label="Groq API Key", type="password")
if not groq_api_key:
    st.info("Please enter your Groq API key to continue.")
    st.stop()

# Initialize LLM
llm = ChatGroq(model="Gemma2-9b-It", groq_api_key=groq_api_key)

# Function to clean non-ASCII characters
def clean_text(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII characters

# Wikipedia Tool
wikipedia_wrapper = WikipediaAPIWrapper()
wikipedia_tool = Tool(
    name="Wikipedia",
    func=lambda query: clean_text(wikipedia_wrapper.run(query)),
    description="A tool for searching Wikipedia for various information on topics mentioned."
)

# Math Tool (Handles arithmetic & algebraic expressions)
math_chain = LLMMathChain.from_llm(llm=llm)
calculator = Tool(
    name="Calculator",
    func=lambda expression: clean_text(math_chain.run(expression)),
    description="A tool for solving math-related questions. Only input mathematical expressions."
)

# Integral Solver (Using LLM)
integral_prompt = """
You are a math expert. Solve the integral of the given function step by step.
Function: {function}
Solution:
"""
integral_template = PromptTemplate(input_variables=["function"], template=integral_prompt)
integral_chain = LLMChain(llm=llm, prompt=integral_template)

integral_solver = Tool(
    name="Integral Solver",
    func=lambda func: clean_text(integral_chain.run({"function": func})),
    description="A tool for solving integrals. Provide a function to integrate."
)

# Reasoning Tool
reasoning_prompt = """
You are an AI agent tasked with solving logical and mathematical reasoning questions.
Provide a step-by-step, detailed explanation for the given question:
Question: {question}
Answer:
"""
reasoning_template = PromptTemplate(input_variables=["question"], template=reasoning_prompt)
reasoning_chain = LLMChain(llm=llm, prompt=reasoning_template)

reasoning_tool = Tool(
    name="Reasoning Tool",
    func=lambda q: clean_text(reasoning_chain.run({"question": q})),
    description="A tool for answering logic-based and reasoning questions."
)

# Initialize the agent with tools
assistant_agent = initialize_agent(
    tools=[wikipedia_tool, calculator, integral_solver, reasoning_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
    handle_parsing_errors=True
)

# Session state for messages
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi, I'm a Math chatbot! Ask me any math-related question!"}
    ]

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg['content'])

# Get user input
question = st.text_area("Enter your question:", "Find the integral of sin(x)")

if st.button("Find My Answer"):
    if question:
        with st.spinner("Generating response..."):
            st.session_state.messages.append({"role": "user", "content": question})
            st.chat_message("user").write(question)

            st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
            response = assistant_agent.run(clean_text(question), callbacks=[st_cb])

            st.session_state.messages.append({'role': 'assistant', "content": response})
            st.write('### Response:')
            st.success(response)
    else:
        st.warning("Please enter a question.")
