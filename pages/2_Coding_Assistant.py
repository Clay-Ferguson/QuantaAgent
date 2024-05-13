""" Streamlit GUI for the Quanta Chatbot """

import streamlit as st
from streamlit_chat import message
from langchain.schema import SystemMessage, HumanMessage, AIMessage

from agent.app_agent import QuantaAgent
from agent.app_config import AppConfig
from agent.utils import Utils


class AppAgentGUI:
    """Streamlit GUI for the Quanta Chatbot."""

    def __init__(self):
        self.cfg = AppConfig.get_config(None)

    def run(self):
        """Main function for the Streamlit GUI."""
        st.set_page_config(page_title="Quanta AI Coding Agent", page_icon="🤖")

        # initialize message history
        if "agent_messages" not in st.session_state:
            st.session_state.agent_messages = []

            st.session_state.agent_messages.append(
                SystemMessage(content="You are a helpful assistant.")
            )

        st.header("Quanta AI Coding Agent 🤖")
        user_input = st.text_area(
            "Your query (Warning: clicking outside this box does a submit): ",
            key="user_input",
        )
        # NOTE: Execution falls thru here even before any text is yet entered

        # handle user input
        if user_input:
            with st.spinner("Thinking..."):
                agent = QuantaAgent()
                agent.run("", st.session_state.agent_messages, user_input)

        # display message history
        messages = st.session_state.get("agent_messages", [])
        for i, msg in enumerate(messages[1:]):
            content = msg.content
            content = Utils.sanitize_content(content)

            # pprint.pprint(msg)
            if isinstance(msg, HumanMessage):
                message(str(content), is_user=True, key=str(i) + "_user")
            elif isinstance(msg, AIMessage):
                message(str(content), is_user=False, key=str(i) + "_ai")


AppAgentGUI().run()
