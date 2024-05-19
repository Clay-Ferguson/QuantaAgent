"""Runs the Agent"""

import streamlit as st

from agent.app_config import AppConfig
from agent.utils import Utils


def show_mode_picker():
    """Show the mode picker."""

    # Define the mapping between keys and display values
    mode_mapping = {
        AppConfig.MODE_FILES: "Whole File",
        AppConfig.MODE_BLOCKS: "Update Blocks",
    }

    # Create the radio button
    st.radio(
        "Coding Assistant Mode:",
        list(mode_mapping.keys()),
        key="p_mode",
        format_func=lambda x: {
            AppConfig.MODE_FILES: "Files: AI is allowed to update entire files.",
            AppConfig.MODE_BLOCKS: "Blocks: AI is only allowed to update specific blocks in the code.",
        }[x],
    )


# to Run: `streamlit run Quanta_Agent.py`

if __name__ == "__main__":
    cfg = AppConfig.get_config(None)

    Utils.setup_page(st, cfg, "Quanta: AI Tools")
    show_mode_picker()

    # Sanity check
    # st.write(st.session_state)
