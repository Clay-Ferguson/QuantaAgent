"""Runs the Agent"""

import streamlit as st
from agent.app_config import AppConfig
from agent.utils import Utils


def show_mode_picker(st):
    """Show the mode picker."""

    # Define the mapping between keys and display values
    mode_mapping = {
        AppConfig.MODE_FILES: "Whole File",
        AppConfig.MODE_BLOCKS: "Update Blocks",
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
        }[x],
        on_change=mode_changed,
    )


def show_ai_model_picker(st):
    """Show the AI model picker."""

    # Define the mapping between keys and display values
    mode_mapping = {
        "openai": "OpenAI",
        "anth": "Anthropic",
    }

    st.radio(
        "Select AI Service:",
        list(mode_mapping.keys()),
        key="p_ai_service",
        format_func=lambda x: {
            "openai": "OpenAI",
            "anth": "Anthropic",
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
