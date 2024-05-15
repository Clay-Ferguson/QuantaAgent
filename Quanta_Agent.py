"""Runs the Agent"""

import streamlit as st

from agent.app_config import AppConfig
from agent.utils import Utils


def show_strategy_picker(default_strategy: str):
    """Show the strategy picker."""

    # Initialize the session state variable if it doesn't exist
    if "update_strategy" not in st.session_state:
        st.session_state.update_strategy = default_strategy

    # Define the mapping between keys and display values
    strategy_mapping = {
        "whole_file": "Whole File",
        "injection_points": "Injection Points",
    }

    idx = list(strategy_mapping.keys()).index(st.session_state.update_strategy)

    # Create the radio button
    choice = st.radio(
        "File Modification Strategy:",
        list(strategy_mapping.keys()),
        index=idx,
        format_func=lambda x: {
            "whole_file": "Whole File: AI is allowed to update entire files.",
            "injection_points": "Injection Points: AI is only allowed to update specific points in the code.",
        }[x],
    )

    # Update the session state variable when the radio button value changes
    st.session_state.update_strategy = choice


# to Run: `streamlit run Quanta_Agent.py`

if __name__ == "__main__":
    cfg = AppConfig.get_config(None)
    Utils.setup_page(st, "Quanta: AI Tools")

    show_strategy_picker(cfg.update_strategy)
