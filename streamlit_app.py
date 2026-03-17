"""
Streamlit UI for the Neo chatbot.
"""

import asyncio
import os
import streamlit as st
from dotenv import load_dotenv

# Load .env so AZURE_OPENAI_* and DEPLOYMENT_NAME are available before importing agent
load_dotenv()

from agent_framework import AgentSession
from agent_framework.exceptions import ChatClientException

from core.agent import create_agent
from main import _is_duplicate_item_error, _clear_session_chat_history

# Page configuration
st.set_page_config(
    page_title="Neo Chatbot",
    page_icon="assets/logo.png",
    layout="centered",
)

col1, col2 = st.columns([1, 8])
with col1:
    st.image("assets/logo.png", width=60)
with col2:
    st.title("Neo Chatbot")
    
st.markdown("💬 **Ask anything, or try some math!** (e.g., 'Add 15 and 30')")

# --- Initialization ---

def initialize_session():
    """Initialize agent, session, and chat history in Streamlit session state."""
    if "agent" not in st.session_state:
        try:
            st.session_state.agent = create_agent()
        except Exception as e:
            st.error(f"Error creating agent: {e}")
            st.stop()
            
    if "agent_session" not in st.session_state:
        # Create a fresh session
        st.session_state.agent_session = st.session_state.agent.create_session()
        
    if "chat_history" not in st.session_state:
        # Store messages to display in the UI (format: {"role": "user"/"assistant", "content": "text"})
        st.session_state.chat_history = []

initialize_session()

# --- Chat UI ---

# Display chat messages from history on app rerun
for message in st.session_state.chat_history:
    avatar = "assets/neo.png" if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask Neo anything..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to UI history
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    # Asynchronous function to run the agent
    async def run_agent_turn(user_input: str, session: AgentSession) -> str | None:
        agent = st.session_state.agent
        
        async def _run():
            return await agent.run(user_input, session=session)

        response = None
        try:
            response = await _run()
        except ChatClientException as e:
            if _is_duplicate_item_error(e):
                _clear_session_chat_history(session)
                try:
                    response = await _run()
                except Exception as retry_ex:
                    st.error(f"Sorry, I hit an error even after retry: {retry_ex}")
            else:
                st.error(f"Sorry, the service reported an error: {e}")
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            
        return response

    # Display assistant response in chat message container
    with st.chat_message("assistant", avatar="assets/neo.png"):
        with st.spinner("Neo is thinking..."):
            response = asyncio.run(run_agent_turn(prompt, st.session_state.agent_session))
            
            if response is not None:
                st.markdown(response)
                # Add assistant response to UI history
                st.session_state.chat_history.append({"role": "assistant", "content": response})

# Sidebar controls
with st.sidebar:
    st.header("Settings")
    if st.button("Clear Chat History"):
        # Reset the session and chart history
        st.session_state.agent_session = st.session_state.agent.create_session()
        st.session_state.chat_history = []
        st.rerun()

