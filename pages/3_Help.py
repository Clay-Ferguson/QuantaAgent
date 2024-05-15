"""Runs the Agent"""

import streamlit as st

from agent.app_config import AppConfig
from agent.utils import Utils

cfg = AppConfig.get_config(None)
Utils.setup_page(st, "Quanta: Agent Help")

# with st.expander("Show Help"):
with open("config/help-text.md", "r", encoding="utf-8") as file:
    help_text: str = file.read()
    st.markdown(help_text)
