"""Settings page."""

import streamlit as st
import argparse
from agent.app_config import AppConfig
from agent.utils import Utils


class Settings:
    """Settings page."""

    def __init__(self):
        self.cfg = None

    def get_config_markdown(self, cfg: argparse.Namespace):
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

    def run(self):
        """Run the settings page."""
        self.cfg = AppConfig.get_config(None)
        Utils.setup_page(st, "Quanta: Agent Settings")

        # ith st.expander("Show Configs"):
        cm = self.get_config_markdown(self.cfg)
        st.markdown(cm)

    # Sanity check
    # st.write(st.session_state)


Settings().run()
