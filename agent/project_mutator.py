"""Injects data into files."""

import os
from typing import List, Dict, Optional
from agent.models import TextBlock
from agent.string_utils import StringUtils
from agent.tags import (
    TAG_BLOCK_BEGIN,
    TAG_BLOCK_END,
    TAG_FILE_BEGIN,
    TAG_FILE_END,
    TAG_NEW_FILE_BEGIN,
    TAG_NEW_FILE_END,
)
from agent.utils import Utils
from agent.app_config import AppConfig


class ProjectMutator:
    """Performs all project mutations that the AI has requested."""

    blocks: Dict[str, TextBlock] = {}

    def __init__(
        self,
        st,
        mode: str,
        source_folder: str,
        ai_answer: str,
        ts: str,
        suffix: Optional[str],
    ):
        """Initializes the ProjectMutator object."""
        self.st = st
        self.mode: str = mode
        self.source_folder: str = source_folder
        self.source_folder_len: int = len(source_folder)
        self.ai_answer: str = ai_answer
        self.suffix: Optional[str] = suffix
        self.ts: str = ts
        self.ran = False
        self.blocks = {}

    def run(self):
        """Performs all the project mutations which may be new files, updated files, or updated blocks in files."""

        if self.ran:
            Utils.fail_app("ProjectMutator has already run.", self.st)
        self.ran = True

        # blocks
        if self.mode == AppConfig.MODE_BLOCKS:
            self.parse_blocks(TAG_BLOCK_BEGIN, TAG_BLOCK_END)
        # files
        elif self.mode == AppConfig.MODE_FILES:
            self.process_new_files()

        self.process_project()

    def parse_blocks(self, begin_tag: str, end_tag: str):
        """Parses the ai answer to find and extract blocks of text defined by '{begin_tag} {Name}'
        and {end_tag}. The output of this method is stored in the 'blocks' dictionary.
        """
        current_block_name: Optional[str] = None
        current_content: List[str] = []
        collecting: bool = False

        for line in self.ai_answer.splitlines():
            line = line.strip()

            if Utils.is_tag_line(line, begin_tag):
                if collecting:
                    Utils.fail_app("Found Begin tag while still collecting", self.st)

                # Start of a new block
                current_block_name = Utils.parse_name_from_tag_line(line, begin_tag)
                collecting = True
                current_content = []

            elif Utils.is_tag_line(line, end_tag):
                # End of the current block
                if current_block_name and collecting:
                    content = "\n".join(current_content)

                    if current_block_name in self.blocks:
                        Utils.fail_app(
                            f"Duplicate Block Name {current_block_name}. LLM is failing sending duplicate blocks in responses.",
                            self.st,
                        )
                    else:
                        self.blocks[current_block_name] = TextBlock(
                            name=current_block_name, content=content
                        )
                else:
                    print("No block name or not collecting")
                collecting = False
                current_block_name = None

            elif collecting:
                # Collect the content of the block
                current_content.append(line)

    def process_new_files(self):
        """
        Parses the ai prompt to find and extract new files content
        defined by '// new_file_begin {Name}' and '// new_file_end' and write those files

        Args:
        text (str): The multiline string containing the file content
        """
        file_name: Optional[str] = None
        file_content: List[str] = []
        collecting: bool = False

        for line in self.ai_answer.splitlines():
            line = line.strip()

            if Utils.is_tag_line(line, f"""{TAG_NEW_FILE_BEGIN} /"""):
                if collecting:
                    Utils.fail_app(
                        "Found New File Begin tag while still collecting", self.st
                    )

                # Start of a new file
                file_name = Utils.parse_name_from_tag_line(line, TAG_NEW_FILE_BEGIN)
                collecting = True
                file_content = []

            elif Utils.is_tag_line(line, f"""{TAG_NEW_FILE_END} /"""):
                # End of the current file
                if file_name and collecting:
                    full_file_name: str = self.source_folder + file_name

                    # Throw error if file exists
                    if os.path.exists(full_file_name):
                        Utils.fail_app(
                            f"Error: The file {full_file_name} already exists. AI accidentally had a filename collision. This is not a bug, just an unfortunate turn of events.",
                            self.st,
                        )

                    # Ensure folder exisits
                    Utils.ensure_folder_exists(full_file_name)

                    # write the new file
                    print("Writing new file: " + full_file_name)
                    Utils.write_file(full_file_name, "\n".join(file_content))
                else:
                    print("No file_name or not collecting")

                collecting = False
                file_name = None

            elif collecting:
                # Collect the content of the file
                file_content.append(line)

    def visit_file(self, filename: str):
        """Visit the file, to run all code modifications on the file"""

        # we need content to be mutable in the methods we pass it to so we hold in a dict
        content: List[str] = [""]
        try:
            # Read the entire file content
            content[0] = Utils.read_file(filename)
            modified: bool = False

            # Check if we have a diff for this file
            rel_filename: str = filename[self.source_folder_len :]
            new_content: Optional[str] = None

            if self.mode == AppConfig.MODE_FILES:
                new_content = self.parse_modified_file(self.ai_answer, rel_filename)

            if new_content is not None:
                content[0] = new_content
                modified = True
            # else if no new content, so we try any block updates
            else:
                if self.mode == AppConfig.MODE_BLOCKS:
                    for name, block in self.blocks.items():
                        if self.replace_blocks(content, block, name):
                            modified = True

            if modified:
                print(f"Updated File: {filename}")

            # Write the modified content back to the file
            if modified:
                out_file: str = (
                    StringUtils.add_filename_suffix(filename, self.suffix)
                    if self.suffix
                    else filename
                )
                Utils.write_file(out_file, content[0])

        except FileNotFoundError:
            print(f"The file {filename} does not exist.")
        except IOError:
            print("An error occurred while reading or writing to the file.")

    def parse_modified_file(self, ai_answer: str, rel_filename: str) -> Optional[str]:
        """Extract the new content for the given file from the AI answer."""

        if f"""{TAG_FILE_BEGIN} {rel_filename}""" not in ai_answer:
            return None

        # Scan all the lines in content one by one and extract the new content
        new_content: List[str] = []
        started: bool = False

        for line in ai_answer.splitlines():
            if started:
                if Utils.is_tag_and_name_line(line, TAG_FILE_END, rel_filename):
                    started = False
                    break
                new_content.append(line)
            elif Utils.is_tag_and_name_line(line, TAG_FILE_BEGIN, rel_filename):
                if len(new_content) > 0:
                    Utils.fail_app(
                        f"Error: {TAG_FILE_BEGIN} {rel_filename} exists multiple times in ai response. The LLM itself is failing.",
                        self.st,
                    )
                started = True

        if len(new_content) == 0:
            return None

        ret: str = "\n".join(new_content)
        return ret

    def replace_blocks(self, content: List[str], block: TextBlock, name: str) -> bool:
        """Process the replacements for the given block."""

        if f"{TAG_BLOCK_BEGIN} {name}" not in content[0]:
            return False

        # we return true here if we did any replacements
        ret: bool = (
            self.replace_block("//", content, block, name)
            or self.replace_block("--", content, block, name)
            or self.replace_block("#", content, block, name)
        )
        return ret

    def replace_block(
        self, comment_prefix: str, content: List[str], block: TextBlock, name: str
    ) -> bool:
        """Process the replacement for the given block and comment prefix. This is what does the actual
        replacement of a named block of code.

        We replace the first element of the dict content with the new content, so we're treating 'content'
        as a mutable object.
        """

        found: bool = False
        lines = content[0].splitlines()
        new_lines = []
        in_block = False
        # We will break up content into lines and then iterate over them to find the block we want to replace
        # We will then replace the block with the new block content
        for line in lines:
            if in_block:
                if f"{comment_prefix} {TAG_BLOCK_END}" in line:
                    in_block = False
                    new_lines.append(block.content)
                    new_lines.append(line)
                    found = True
            elif f"{comment_prefix} {TAG_BLOCK_BEGIN} {name}" in line:
                in_block = True
                new_lines.append(line)
            else:
                new_lines.append(line)

        if found:
            content[0] = "\n".join(new_lines)

        return found

    def process_project(self):
        """Scans the directory for files with the specified extensions."""

        # Walk through all directories and files in the directory
        for dirpath, _, filenames in os.walk(self.source_folder):
            for filename in filenames:
                # Check the file extension
                if Utils.should_include_file(AppConfig.ext_set, filename):
                    # build the full path
                    path: str = os.path.join(dirpath, filename)
                    # Call the visitor function for each file
                    self.visit_file(path)
