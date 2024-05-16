import streamlit as st

from agent.app_config import AppConfig
from agent.utils import Utils

# TODO: Just for consistency make this a class like other pages


def get_config_markdown(cfg):
    """Get the config markdown."""
    return f"""
### Configuration
* Model: {cfg.openai_model}
* Source Folder: {cfg.source_folder}
* Data Folder: {cfg.data_folder}
* Extensiont to include: {cfg.scan_extensions}
* Update Strategy: {cfg.update_strategy}
* Max Prompt Length: {cfg.max_prompt_length}
"""


cfg = AppConfig.get_config(None)
Utils.setup_page(st, "Quanta: Agent Settings")

# ith st.expander("Show Configs"):
cm = get_config_markdown(cfg)
st.markdown(cm)

# Sanity check
# st.write(st.session_state)
