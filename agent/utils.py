"""Utilities Module"""

from io import TextIOWrapper
import re
import os
import argparse
from typing import List, Set, Optional
import streamlit as st
from agent.app_config import AppConfig
from agent.tags import (
    TAG_FILE_BEGIN,
    TAG_FILE_END,
    TAG_NEW_FILE_BEGIN,
    TAG_NEW_FILE_END,
    TAG_BLOCK_BEGIN,
    TAG_BLOCK_END,
)


class Utils:
    """Utilities Class"""

    @staticmethod
    def open_file(filename: str) -> TextIOWrapper:
        """Reads a file and returns the content."""
        return open(filename, "r", encoding="utf-8")

    @staticmethod
    def write_file(filename: str, content: str):
        """Writes content to a file."""

        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)

    @staticmethod
    def read_file(filename: str) -> str:
        """Reads a file and returns the content."""
        with Utils.open_file(filename) as file:
            return file.read()

    @staticmethod
    def should_include_file(ext_set: Set[str], file_name: str) -> bool:
        """Returns True if the file should be included in the scan."""
        # return file_name.endswith(tuple(AppConfig.ext_set)) # <--- AI suggested this. Didn't investigate further
        _, ext = os.path.splitext(file_name)
        return ext.lower() in ext_set

    @staticmethod
    def has_tag_lines(prompt: str, tag: str) -> bool:
        """Checks if the prompt has this tag line."""

        # Note: the 're' module caches compiled regexes, so there's no need to store the compiled regex for reuse.
        pattern: str = rf"^(-- |// |# |) {re.escape(tag)} "
        return re.search(pattern, prompt) is not None

    @staticmethod
    def has_new_files(content: str) -> bool:
        """Checks if the content has new files."""
        return (
            f"""{TAG_NEW_FILE_BEGIN} /""" in content
            and f"""{TAG_NEW_FILE_END} /""" in content
        )

    @staticmethod
    def is_tag_and_name_line(line: str, tag: str, name: str) -> bool:
        """Checks if the line is a pattern like
        `-- block_begin {Name}` or `// block_begin {Name}` or `# block_begin {Name}`
        or `-- block_end {Name}` or `// block_end {Name}` or `# block_end {Name}`
        or any of those without the comment characters at the beginning of the line as well
        """

        # Note: the 're' module caches compiled regexes, so there's no need to store the compiled regex for reuse.
        pattern: str = rf"^(-- |// |# |){re.escape(tag)} {name}$"
        return re.search(pattern, line) is not None

    # If the line is something like "// block_begin name" we return name, else return None
    @staticmethod
    def parse_name_from_tag_line(line: str, tag: str) -> Optional[str]:
        """Parses the name from a `... {tag} {name}` formatted line."""
        pattern: str = rf"^(-- |// |# |){re.escape(tag)}(.+)$"
        match = re.search(pattern, line)
        if match:
            return match.group(2).strip()
        else:
            return None

    # NOTE: if exact=True it does an exact match on this line, else functions more like a "startswith"
    #       Note: This means is exact=true we're checking the nothing is to the right of the tag.
    @staticmethod
    def is_tag_line(line: str, tag: str) -> bool:
        """Checks if the line is a line like
        `-- block_begin` or `// block_begin` or `# block_begin`
        or `-- block_end` or `// block_end` or `# block_end`
        or any of those without the comment characters at the beginning of the line as well

        Notice that we only check for the tag, not the block name.
        """

        # Note: the 're' module caches compiled regexes, so there's no need to store the compiled regex for reuse.
        pattern: str = rf"^(-- |// |# |){re.escape(tag)}"

        # Forces our pattren to apply out to the end of the string (making it an exact match)
        # if exact:
        #     pattern += "$"
        return re.search(pattern, line) is not None

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
    def sanitize_content(cfg: argparse.Namespace, content: str) -> str:
        """Makes an AI response string presentable in on screen."""

        # Scan all the lines in content one by one and extract the new content
        new_content: List[str] = []

        # to support blocks in blocks we use a counter to keep track of how many blocks we're in
        started_counter: int = 0
        block_mode = cfg.mode == AppConfig.MODE_BLOCKS

        for line in content.splitlines():
            # ENDS
            if Utils.is_tag_line(line, TAG_FILE_END):
                started_counter -= 1
            elif Utils.is_tag_line(line, TAG_NEW_FILE_END):
                started_counter -= 1
            elif block_mode and Utils.is_tag_line(line, TAG_BLOCK_END):
                started_counter -= 1

            # BEGINS
            elif Utils.is_tag_line(line, TAG_FILE_BEGIN):
                name: Optional[str] = Utils.parse_name_from_tag_line(
                    line, TAG_FILE_BEGIN
                )
                started_counter += 1
                if started_counter == 1:
                    new_content.append(f"File Updated: {name}")

            elif Utils.is_tag_line(line, TAG_NEW_FILE_BEGIN):
                name: Optional[str] = Utils.parse_name_from_tag_line(
                    line, TAG_NEW_FILE_BEGIN
                )
                started_counter += 1
                if started_counter == 1:
                    new_content.append(f"File Created: {name}")

            elif block_mode and Utils.is_tag_line(line, TAG_BLOCK_BEGIN):
                name: Optional[str] = Utils.parse_name_from_tag_line(
                    line, TAG_BLOCK_BEGIN
                )
                started_counter += 1
                if started_counter == 1:
                    new_content.append(f"Code Block Updated: {name}")

            elif started_counter == 0:
                new_content.append(line)

        ret: str = "\n".join(new_content)
        return ret

    @staticmethod
    def setup_page(st, cfg: argparse.Namespace, title: str):
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

        Utils.set_default_session_vars(cfg)
        Utils.keep_session_vars()

    @staticmethod
    def set_default_session_vars(cfg: argparse.Namespace):
        """Sets the default session variables."""
        if "p_mode" not in st.session_state:
            st.session_state.p_mode = cfg.mode
        if "p_source_provided" not in st.session_state:
            st.session_state.p_source_provided = False
        if "p_agent_user_input" not in st.session_state:
            st.session_state.p_agent_user_input = ""

    @staticmethod
    def keep_session_vars():
        """
        Keeps the session state variables from being deleted by Streamlit.

        This is a workaround for the issue where Streamlit deletes session state variables when the page is refreshed.
        https://discuss.streamlit.io/t/mutipages-and-st-session-state-has-no-key-username/45237
        """
        for prop in st.session_state:
            if prop.startswith("p_"):
                st.session_state[prop] = st.session_state[prop]

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
