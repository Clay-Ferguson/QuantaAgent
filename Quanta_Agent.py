"""Runs the Agent"""

import streamlit as st

from agent.app_config import AppConfig
from agent.utils import Utils


def show_strategy_picker():
    """Show the strategy picker."""

    # Define the mapping between keys and display values
    strategy_mapping = {
        "whole_file": "Whole File",
        "injection_points": "Injection Points",
    }

    # Create the radio button
    st.radio(
        "File Modification Strategy:",
        list(strategy_mapping.keys()),
        key="p_update_strategy",
        format_func=lambda x: {
            "whole_file": "Whole File: AI is allowed to update entire files.",
            "injection_points": "Injection Points: AI is only allowed to update specific points in the code.",
        }[x],
    )


# to Run: `streamlit run Quanta_Agent.py`

if __name__ == "__main__":
    cfg = AppConfig.get_config(None)

    Utils.setup_page(st, cfg, "Quanta: AI Tools")
    show_strategy_picker()

    # Sanity check
    # st.write(st.session_state)
