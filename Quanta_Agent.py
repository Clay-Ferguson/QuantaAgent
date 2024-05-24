"""Runs the Agent"""

import streamlit as st
from agent.app_config import AppConfig
from agent.utils import Utils, AIService


def show_mode_picker(st):
    """Show the mode picker."""

    # Define the mapping between keys and display values
    mode_mapping = {
        AppConfig.MODE_FILES: "Whole File",
        AppConfig.MODE_BLOCKS: "Update Blocks",
        AppConfig.MODE_NONE: "None",
    }

    def mode_changed():
        Utils.clear_agent_state()

    st.radio(
        "Coding Assistant Mode:",
        list(mode_mapping.keys()),
        key="p_mode",
        format_func=lambda x: {
            AppConfig.MODE_FILES: "Files: AI is allowed to update entire files.",
            AppConfig.MODE_BLOCKS: "Blocks: AI is only allowed to update specific blocks in the code.",
            AppConfig.MODE_NONE: "None: No Code Refactoring",
        }[x],
        on_change=mode_changed,
    )


def show_ai_model_picker(st):
    """Show the AI model picker."""

    # Define the mapping between keys and display values
    mode_mapping = {
        AIService.OPENAI.value: "OpenAI",
        AIService.ANTHROPIC.value: "Anthropic",
    }

    st.radio(
        "Select AI Service:",
        list(mode_mapping.keys()),
        key="p_ai_service",
        format_func=lambda x: {
            AIService.OPENAI.value: "OpenAI",
            AIService.ANTHROPIC.value: "Anthropic",
        }[x],
        # on_change=mode_changed,
    )


# to Run: `streamlit run Quanta_Agent.py`

if __name__ == "__main__":
    cfg = AppConfig.get_config(None)

    Utils.setup_page(st, cfg, "Quanta: AI Tools")
    show_ai_model_picker(st)
    show_mode_picker(st)

    # Sanity check
    # st.write(st.session_state)
