import streamlit as st

from agent.app_config import AppConfig
from agent.utils import Utils

# Define the files lookup map
files = {
    "README.md": "Readme Text / Introduction",
    "config/help-text.md": "Coding Assistant Tips",
    "docs/named-blocks.md": "Named Blocks",
    "docs/injection-points.md": "Injection Points",
}


class Documentation:
    """Streamlit GUI for the Quanta Chatbot."""

    def __init__(self):
        self.cfg = AppConfig.get_config(None)

    def read_file(self, file_path: str):
        """Read the content of a file."""
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return content

    def run(self):
        ### Main Documentation Page ###
        Utils.setup_page(st, self.cfg, "Quanta: Documentation")

        # Create a two-column layout
        col1, col2 = st.columns([1, 3])

        # Display the list of files in the left column
        with col1:
            selected_file = list(files.keys())[0]  # Set default selected file
            for file_path, friendly_name in files.items():
                if st.button(friendly_name):
                    selected_file = file_path

        # Display the content of the selected file in the right column
        with col2:
            content = self.read_file(selected_file)
            Utils.st_markdown(content)

        # Sanity check
        # st.write(st.session_state)


Documentation().run()
