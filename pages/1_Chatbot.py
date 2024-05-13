""" Streamlit GUI for the Quanta Chatbot """

import streamlit as st
from streamlit_chat import message
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from agent.app_config import AppConfig


class AppChatbotGUI:
    """Streamlit GUI for the Quanta Chatbot."""

    def __init__(self):
        self.cfg = AppConfig.get_config(None)

    def run(self):
        """Main function for the Streamlit GUI."""
        st.set_page_config(page_title="Quanta AI Chatbot", page_icon="🤖")

        chat = ChatOpenAI(
            model=self.cfg.openai_model, temperature=0, api_key=self.cfg.openai_api_key
        )

        # initialize message history
        if "chatbot_messages" not in st.session_state:
            st.session_state.chatbot_messages = []

            st.session_state.chatbot_messages.append(
                SystemMessage(content="You are a helpful assistant.")
            )

        st.header("Quanta AI Chatbot 🤖")
        user_input = st.text_area(
            "Your query (Warning: clicking outside this box does a submit): ",
            key="user_input",
        )

        # handle user input
        if user_input:
            st.session_state.chatbot_messages.append(HumanMessage(content=user_input))
            with st.spinner("Thinking..."):
                response = chat(list(st.session_state.chatbot_messages))

            st.session_state.chatbot_messages.append(
                AIMessage(content=response.content)
            )

        # display message history
        messages = st.session_state.get("chatbot_messages", [])
        for i, msg in enumerate(messages[1:]):
            # pprint.pprint(msg)
            if isinstance(msg, HumanMessage):
                message(str(msg.content), is_user=True, key=str(i) + "_user")
            elif isinstance(msg, AIMessage):
                message(str(msg.content), is_user=False, key=str(i) + "_ai")


AppChatbotGUI().run()
