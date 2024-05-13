""" Streamlit GUI for the Quanta Chatbot """

import streamlit as st
from streamlit_chat import message
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from agent.app_config import AppConfig
from agent.utils import Utils


class AppChatbotGUI:
    """Streamlit GUI for the Quanta Chatbot."""

    def __init__(self):
        self.cfg = AppConfig.get_config(None)

    def clear_all(self):
        """Clear all messages."""
        st.session_state.chatbot_messages = []

        # TODO: make this page have 'chat_user_input' instead of 'user_input', and other page similar rename
        st.session_state.user_input = ""

    def ask_ai(self):
        """Ask the AI."""
        # initialize message history
        if "chatbot_messages" not in st.session_state:
            st.session_state.chatbot_messages = []

            st.session_state.chatbot_messages.append(
                SystemMessage(content="You are a helpful assistant.")
            )

        # handle user input
        user_input = st.session_state.user_input
        # handle user input
        if user_input:
            if len(user_input) > int(self.cfg.max_prompt_length):
                st.error(
                    f"Input is too long. Max allowed is {self.cfg.max_prompt_length} characters."
                )
                return

            st.session_state.chatbot_messages.append(HumanMessage(content=user_input))
            with st.spinner("Thinking..."):
                chat = ChatOpenAI(
                    model=self.cfg.openai_model,
                    temperature=0,
                    api_key=self.cfg.openai_api_key,
                )
                response = chat(list(st.session_state.chatbot_messages))

            st.session_state.chatbot_messages.append(
                AIMessage(content=response.content)
            )
            st.session_state.user_input = ""  # Clear the user input after processing

    def show_messages(self):
        """display message history"""
        messages = st.session_state.get("chatbot_messages", [])
        for i, msg in enumerate(messages[1:]):
            if isinstance(msg, HumanMessage):
                message(str(msg.content), is_user=True, key=str(i) + "_user")
            elif isinstance(msg, AIMessage):
                message(str(msg.content), is_user=False, key=str(i) + "_ai")

    def run(self):
        """Main function for the Streamlit GUI."""
        Utils.setup_page(st, "Quanta: AI Chatbot")

        with st.form("chatbot_form"):
            st.text_area(
                "Ask the AI a Question: ",
                key="user_input",
            )
            col1, col2 = st.columns(2)
            with col1:
                st.form_submit_button("Ask AI", on_click=self.ask_ai)
            with col2:
                st.form_submit_button("Clear", on_click=self.clear_all)

        self.show_messages()


AppChatbotGUI().run()
