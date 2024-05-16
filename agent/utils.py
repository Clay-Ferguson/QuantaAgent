"""Utilities Module"""

import re
import os
from typing import List, Set
import streamlit as st
from agent.tags import (
    TAG_INJECT_END,
    TAG_INJECT_BEGIN,
    TAG_FILE_BEGIN,
    TAG_FILE_END,
    TAG_NEW_FILE_BEGIN,
    TAG_NEW_FILE_END,
)


class Utils:
    """Utilities Class"""

    @staticmethod
    def should_include_file(ext_set: Set[str], file_name: str) -> bool:
        """Returns True if the file should be included in the scan."""
        # return file_name.endswith(tuple(AppConfig.ext_set)) # <--- AI suggested this. Didn't investigate further
        _, ext = os.path.splitext(file_name)
        return ext.lower() in ext_set

    @staticmethod
    def has_tag_lines(prompt: str, tag: str) -> bool:
        """Checks if the prompt has any block_inject tags."""

        # Note: the 're' module caches compiled regexes, so there's no need to store the compiled regex for reuse.
        pattern: str = rf"(--|//|#) {re.escape(tag)} "
        return re.search(pattern, prompt) is not None

    @staticmethod
    def has_filename_injects(prompt: str, file_names: List[str]) -> bool:
        """Returns True if the prompt has any file content injection."""
        for file_name in file_names:
            tag_begin: str = f"{TAG_FILE_BEGIN} {file_name}"
            tag_end: str = f"{TAG_FILE_END} {file_name}"
            if tag_begin in prompt and tag_end in prompt:
                return True
        return False

    @staticmethod
    def has_folder_injects(prompt: str, folder_names: List[str]) -> bool:
        """Returns True if the prompt has any folder content injection."""
        for folder_name in folder_names:
            tag: str = f"${{{folder_name}/}}"
            if tag in prompt:
                print(f"Found folder inject tag: {tag}")
                return True
        return False

    @staticmethod
    def has_new_files(content: str) -> bool:
        """Checks if the content has new files."""
        return (
            f"""{TAG_NEW_FILE_BEGIN} /""" in content
            and f"""{TAG_NEW_FILE_END} /""" in content
        )

    @staticmethod
    def is_tag_and_name_line(line: str, tag: str, name: str) -> bool:
        """Checks if the line is a line like
        `-- block_begin {Name}` or `// block_begin {Name}` or `# block_begin {Name}`
        or `-- block_end {Name}` or `// block_end {Name}` or `# block_end {Name}`
        """

        # Note: the 're' module caches compiled regexes, so there's no need to store the compiled regex for reuse.
        pattern: str = rf"^(--|//|#) {re.escape(tag)} {name}"
        return re.search(pattern, line) is not None

    @staticmethod
    def is_tag_line(line: str, tag: str) -> bool:
        """Checks if the line is a line like
        `-- block_begin {Name}` or `// block_begin {Name}` or `# block_begin {Name}`
        or `-- block_end {Name}` or `// block_end {Name}` or `# block_end {Name}`

        Notice that we only check for the tag, not the block name.
        """

        # Note: the 're' module caches compiled regexes, so there's no need to store the compiled regex for reuse.
        pattern: str = rf"^(--|//|#) {re.escape(tag)}"
        return re.search(pattern, line) is not None

    @staticmethod
    def parse_block_name_from_line(line: str, tag: str) -> str:
        """Parses the block name from a `... {tag} {name}` formatted line."""
        index: int = line.find(f"{tag} ")
        return line[index + len(tag) :].strip()

    @staticmethod
    def fail_app(msg: str, st=None):
        """Exits the application with a fail message"""

        if st is not None:
            st.error(f"Error: {msg}")
        else:
            print(f"Error: {msg}")
            exit(1)

    @staticmethod
    def ensure_folder_exists(file_path: str):
        """Ensures that the folder for the file exists."""
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def sanitize_content(content: str) -> str:
        """Makes an AI input or output string presentable in on screen."""

        # Scan all the lines in content one by one and extract the new content
        new_content: List[str] = []
        started: bool = False

        for line in content.splitlines():
            if Utils.is_tag_line(line, TAG_FILE_END):
                started = False
                break
            elif Utils.is_tag_line(line, TAG_NEW_FILE_END):
                started = False
                break
            elif Utils.is_tag_line(line, TAG_INJECT_END):
                started = False
                break

            elif Utils.is_tag_line(line, TAG_FILE_BEGIN):
                name = Utils.parse_block_name_from_line(line, TAG_FILE_BEGIN)
                started = True
                new_content.append("File Updated: " + name)

            elif Utils.is_tag_line(line, TAG_NEW_FILE_BEGIN):
                name = Utils.parse_block_name_from_line(line, TAG_NEW_FILE_BEGIN)
                started = True
                new_content.append("File Created: " + name)

            elif Utils.is_tag_line(line, TAG_INJECT_BEGIN):
                name = Utils.parse_block_name_from_line(line, TAG_INJECT_BEGIN)
                started = True
                new_content.append("Code Block Updated: " + name)

            elif started is False:
                new_content.append(line)

        ret: str = "\n".join(new_content)
        return ret

    @staticmethod
    def setup_page(st, title: str):
        """Displays the app header and configures the page."""
        st.set_page_config(page_title=title, page_icon="🤖", layout="wide")

        # Create a multi-column layout
        col1, col2 = st.columns([4, 1])

        # Display the header in the first column
        with col1:
            st.header(title)

        # Display the logo image in the second column
        with col2:
            st.image("img/logo-100px-tr.jpg", width=100)

        # All Session Vars that are shared acorss pages should be include here or else they
        # will be lost when the user navigates to another page.
        # This is a rediculous fix to stop the Streamlit API from blowing away this varible.
        # Some moron at Streamlit decided that if a variable is not used in the current scope, it should be deleted
        # from the session state, but it's completely stupid to randomly delete variables like that. Lucikly one of their
        # developers provided this hack of a workaround:
        # https://discuss.streamlit.io/t/mutipages-and-st-session-state-has-no-key-username/45237
        Utils.keep_session_vars(
            "update_strategy",
            "chatbot_messages",
            "agent_messages",
        )

    @staticmethod
    def keep_session_vars(*property_names: str):
        """Keeps the session state variables from being deleted by Streamlit."""
        for property_name in property_names:
            if property_name in st.session_state:
                st.session_state[property_name] = st.session_state[property_name]

    @staticmethod
    def st_markdown(markdown_string):
        """Renders markdown with images in Streamlit.
        We need this method only because Streamlit's markdown does not support localhost images.
        """
        parts = re.split(r"!\[(.*?)\]\((.*?)\)", markdown_string)
        for i, part in enumerate(parts):
            if i % 3 == 0:
                st.markdown(part)
            elif i % 3 == 1:
                title = part
            else:
                st.image(part)  # Add caption if you want -> , caption=title)
