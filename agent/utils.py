"""Utilities Module"""

import re
import os
from typing import List, Set
from agent.tags import (
    TAG_INJECT_END,
    TAG_INJECT_BEGIN,
    TAG_FILE_BEGIN,
    TAG_FILE_END,
    TAG_NEW_FILE_BEGIN,
    TAG_NEW_FILE_END,
    DIVIDER,
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

    # TODO: what type is 'st' (streamlit object)?
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

    # TODO: need to rethink this formatter, if the user is mentioning spcific blocks, folders, or files
    # inside the prompt we need to keep the context of all that by inserting something like:
    # "File: {file_name}..., Block: {block_name}..., Folder: {folder_name}..."
    @staticmethod
    def sanitize_content(content: str) -> str:
        """Makes an AI input or output string presentable in on screen."""

        content = content.split(DIVIDER)[0]

        # Scan all the lines in content one by one and extract the new content
        new_content: List[str] = []
        started: bool = False
        addendum: List[str] = []

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
        if addendum:
            ret += "\n\n" + "\n".join(addendum)
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
