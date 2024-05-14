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
from agent.prompt_templates import PromptTemplates


class Utils:
    """Utilities Class"""

    @staticmethod
    def has_tag_lines(prompt, tag: str) -> bool:
        """Checks if the prompt has any block_inject tags."""

        # Note: the 're' module caches compiled regexes, so there's no need to store the compiled regex for reuse.
        pattern = rf"(--|//|#) {re.escape(tag)} "
        return re.search(pattern, prompt) is not None

    @staticmethod
    def has_filename_injects(prompt, file_names: List[str]) -> bool:
        """Returns True if the prompt has any file content injection."""
        for file_name in file_names:
            tag_begin = f"{TAG_FILE_BEGIN} {file_name}"
            tag_end = f"{TAG_FILE_END} {file_name}"
            if tag_begin in prompt and tag_end in prompt:
                return True
        return False

    @staticmethod
    def has_folder_injects(prompt, folder_names: List[str]) -> bool:
        """Returns True if the prompt has any folder content injection."""
        for folder_name in folder_names:
            tag = f"${{{folder_name}/}}"
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
    def is_tag_and_name_line(line, tag: str, name: str) -> bool:
        """Checks if the line is a line like
        `-- block_begin {Name}` or `// block_begin {Name}` or `# block_begin {Name}`
        or `-- block_end {Name}` or `// block_end {Name}` or `# block_end {Name}`
        """

        # Note: the 're' module caches compiled regexes, so there's no need to store the compiled regex for reuse.
        pattern = rf"^(--|//|#) {re.escape(tag)} {name}"
        return re.search(pattern, line) is not None

    @staticmethod
    def is_tag_line(line: str, tag: str) -> bool:
        """Checks if the line is a line like
        `-- block_begin {Name}` or `// block_begin {Name}` or `# block_begin {Name}`
        or `-- block_end {Name}` or `// block_end {Name}` or `# block_end {Name}`

        Notice that we only check for the tag, not the block name.
        """

        # Note: the 're' module caches compiled regexes, so there's no need to store the compiled regex for reuse.
        pattern = rf"^(--|//|#) {re.escape(tag)}"
        return re.search(pattern, line) is not None

    @staticmethod
    def parse_block_name_from_line(line: str, tag: str) -> str:
        """Parses the block name from a `... {tag} {name}` formatted line."""
        index = line.find(f"{tag} ")
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

        content = content.split(DIVIDER)[0]

        # Scan all the lines in content one by one and extract the new content
        new_content = []
        started = False
        addendum = []
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

        ret = "\n".join(new_content)
        if addendum:
            ret += "\n\n" + "\n".join(addendum)
        return ret

    @staticmethod
    def insert_files_into_prompt(
        prompt: str, source_folder: str, file_names: List[str]
    ) -> str:
        """
        Substitute entire file contents into the prompt. Prompts can contain ${FileName} tags,
        which will be replaced with the content of the file with the name 'FileName'
        """
        for file_name in file_names:
            tag = f"${{{file_name}}}"
            if tag in prompt:
                with open(source_folder + file_name, "r", encoding="utf-8") as file:
                    content = file.read()
                    prompt = prompt.replace(
                        tag, PromptTemplates.get_file_content_block(file_name, content)
                    )

        return prompt

    @staticmethod
    def insert_folders_into_prompt(
        prompt: str, source_folder: str, folder_names: List[str], ext_set: Set[str]
    ):
        """
        Substitute entire folder contents into the prompt. Prompts can contain ${FolderName} tags,
        which will be replaced with the content of the files inside the folder
        """
        source_folder_len = len(source_folder)
        for folder_name in folder_names:
            tag = f"${{{folder_name}/}}"
            # print(f"Checking for folder tag: {tag}")
            if tag in prompt:
                # build the content of the folder (that -1 is removing the trailing slash from the folder name)
                content = PromptTemplates.build_folder_content(
                    source_folder + folder_name,
                    ext_set,
                    source_folder_len,
                )
                prompt = prompt.replace(tag, content)

        return prompt

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
            logo_image = "img/logo-100px-tr.jpg"
            st.image(logo_image, width=100)
