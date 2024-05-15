"""Runs the Agent"""

import streamlit as st

from agent.app_config import AppConfig
from agent.utils import Utils


def get_config_markdown(cfg):
    """Get the config markdown."""
    return f"""
### Config:
* Model: {cfg.openai_model}
* Source Folder: {cfg.source_folder}
* Data Folder: {cfg.data_folder}
* Extensiont to include: {cfg.scan_extensions}
* Update Strategy: {cfg.update_strategy}
* Max Prompt Length: {cfg.max_prompt_length}
"""


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
    st.markdown("Choose an AI tool to use from the sidebar.")

    show_strategy_picker(cfg.update_strategy)

    with st.expander("Expand for Helpful Tips"):
        st.markdown(
            """
### Chatbot:

The chatbot doesn't refactor code but is just a basic chatbot for general purpose conversation.

### Coding Assistant:

The Coding Assistant is also a general chatbot as well however it can also refactor code. You need to provide name of the project folder of the code you want to refactor, in the 
`config.yaml`

**Coding Assistant Tips:**

* To refactor your project files you need to mention `${/}`, which will bring all your project files into the AI's context, and
allow any arbitrary changes, but beware this uses up more of your AI credits. *Note: Your content after the ${/} will get omitted from the GUI,
but it will be used by the AI.*

* To refactor a folder, you can use `${/folder_name/}` to bring all the files in that folder into the AI's context. Note that this
must end with a slash. *Note: The folder content is omitted from the GUI display, but it will be used by the AI.*

* To refactor a specific file, you can use `${/file_name}` to bring that file into the AI's context. *Note: The file content is omitted from the GUI display, but it will be used by the AI.*

"""
        )

    with st.expander("Show Configs"):
        cm = get_config_markdown(cfg)
        st.markdown(cm)
