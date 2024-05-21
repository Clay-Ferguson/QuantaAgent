""" Streamlit GUI for the Quanta Chatbot """

from typing import List
import streamlit as st
from streamlit_chat import message
from langchain.schema import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI

from agent.app_config import AppConfig
from agent.utils import Utils


class AppChatbotGUI:
    """Streamlit GUI for the Quanta Chatbot."""

    def __init__(self):
        self.cfg = AppConfig.get_config(None)

    def clear_all(self):
        """Clear all messages."""
        messages: List[BaseMessage] = []
        st.session_state.p_chatbot_messages = messages
        st.session_state.p_chatbot_user_input = ""

    def ask_ai(self):
        """Ask the AI."""
        # initialize message history
        if "p_chatbot_messages" not in st.session_state:
            messages: List[BaseMessage] = []
            st.session_state.p_chatbot_messages = messages

            st.session_state.p_chatbot_messages.append(
                SystemMessage(content="You are a helpful assistant.")
            )

        # handle user input
        user_input: str = st.session_state.p_chatbot_user_input
        if user_input:
            if len(user_input) > int(self.cfg.max_prompt_length):
                st.error(
                    f"Input is too long. Max allowed is {self.cfg.max_prompt_length} characters."
                )
                return

            st.session_state.p_chatbot_messages.append(HumanMessage(content=user_input))
            with st.spinner("Thinking..."):
                chat = ChatOpenAI(
                    model=self.cfg.openai_model,
                    temperature=0.7,
                    api_key=self.cfg.openai_api_key,
                )
                response = chat.invoke(list(st.session_state.p_chatbot_messages))

            st.session_state.p_chatbot_messages.append(
                AIMessage(content=response.content)
            )
            st.session_state.p_chatbot_user_input = (
                ""  # Clear the user input after processing
            )

    def show_messages(self):
        """display message history"""
        messages = st.session_state.get("p_chatbot_messages", [])
        for i, msg in enumerate(messages[1:]):
            if isinstance(msg, HumanMessage):
                message(str(msg.content), is_user=True, key=str(i) + "_user")
            elif isinstance(msg, AIMessage):
                message(str(msg.content), is_user=False, key=str(i) + "_ai")

    def show_form(self):
        """Show the form to ask the AI a question."""
        with st.form("chatbot_form"):
            st.text_area(
                "Ask the AI a Question: ",
                key="p_chatbot_user_input",
            )
            col1, col2 = st.columns(2)
            with col1:
                st.form_submit_button("Ask AI", on_click=self.ask_ai)
            with col2:
                st.form_submit_button("Clear", on_click=self.clear_all)

    def run(self):
        """Main function for the Streamlit GUI."""
        Utils.setup_page(st, self.cfg, "Quanta: AI Chatbot")

        self.show_messages()
        self.show_form()

        # Sanity check
        # st.write(st.session_state)


AppChatbotGUI().run()
