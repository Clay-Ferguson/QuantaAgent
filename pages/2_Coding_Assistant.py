""" Streamlit GUI for the Quanta Chatbot """

from typing import List
import streamlit as st
from streamlit_chat import message
from langchain.schema import SystemMessage, HumanMessage, AIMessage, BaseMessage

from agent.app_agent import QuantaAgent
from agent.app_config import AppConfig
from agent.prompt_utils import PromptUtils
from agent.utils import Utils


class AppAgentGUI:
    """Streamlit GUI for the Quanta Chatbot."""

    def __init__(self):
        self.cfg = AppConfig.get_config(None)

    def clear_all(self):
        """Clear all messages."""
        messages: List[BaseMessage] = []
        st.session_state.p_agent_messages = messages
        st.session_state.agent_user_input = ""
        PromptUtils.user_inputs = {}

    def ask_ai(self):
        """Ask the AI."""
        # initialize message history
        if "p_agent_messages" not in st.session_state:
            messages: List[BaseMessage] = []
            st.session_state.p_agent_messages = messages

            st.session_state.p_agent_messages.append(
                SystemMessage(content="You are a helpful assistant.")
            )

        # handle user input
        user_input = st.session_state.agent_user_input
        if user_input:
            with st.spinner("Thinking..."):
                agent = QuantaAgent()
                agent.run(
                    st,
                    st.session_state.p_mode,
                    "",
                    st.session_state.p_agent_messages,
                    user_input,
                )
            st.session_state.agent_user_input = ""

    def show_messages(self):
        """display message history"""
        default_messages: List[BaseMessage] = []
        messages = st.session_state.get("p_agent_messages", default_messages)
        for i, msg in enumerate(messages[1:]):
            if isinstance(msg, HumanMessage):

                # I'm not sure if this is a bug or what, when this message is missing, but if so it's related
                # to clearing the messages with the clear button
                # if id(msg) is not in user_inputs, just make user_input be "message gone"
                if id(msg) not in PromptUtils.user_inputs:
                    PromptUtils.user_inputs[id(msg)] = "Message Gone"

                user_input = PromptUtils.user_inputs[id(msg)]
                message(user_input, is_user=True, key=str(i) + "_user")
            elif isinstance(msg, AIMessage):
                content: str = msg.content  # type: ignore
                content = Utils.sanitize_content(self.cfg, content)
                message(str(content), is_user=False, key=str(i) + "_ai")

    def show_form(self):
        """Show the form for user input."""
        with st.form("agent_form"):
            st.text_area(
                "Ask the AI a Question (or ask for a Code Refactor to be done): ",
                key="agent_user_input",
            )
            col1, col2 = st.columns(2)
            with col1:
                st.form_submit_button("Ask AI", on_click=self.ask_ai)
            with col2:
                st.form_submit_button("Clear", on_click=self.clear_all)

    def run(self):
        """Main function for the Streamlit GUI."""
        Utils.setup_page(st, self.cfg, "Quanta: AI Coding Agent")

        self.show_messages()
        self.show_form()

        with st.expander("Helpful Tips. Read this first!"):
            st.markdown(PromptUtils.get_template("config/agent_chat_tips"))

        # Sanity check
        # st.write(st.session_state)


AppAgentGUI().run()
