import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent'))
from agent import run_agent

st.set_page_config(
    page_title="Portfolio Intelligence Agent",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Portfolio Intelligence Agent")
st.caption("Multi-cloud analytics system | AWS S3 · Azure · DuckDB · LangGraph")
st.divider()

with st.sidebar:
    st.header("Try these questions")
    questions = [
        "Which stock has the best Sharpe ratio?",
        "Show me the top 5 performers by return",
        "Which stocks are the most volatile?",
        "Compare AAPL and MSFT performance",
        "Which stocks are underperforming?",
    ]
    for q in questions:
        if st.button(q, use_container_width=True):
            st.session_state.pending = q

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending" not in st.session_state:
    st.session_state.pending = None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("steps"):
            with st.expander("Agent reasoning"):
                for step in msg["steps"]:
                    st.code(step)

question = st.chat_input("Ask anything about the portfolio...")

if st.session_state.pending:
    question = st.session_state.pending
    st.session_state.pending = None

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            result = run_agent(question)

        st.write(result["answer"])

        if result["steps"]:
            with st.expander("Agent reasoning"):
                for step in result["steps"]:
                    st.code(step)

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "steps": result["steps"]
    })