"""This is the main agent module that scans the source code and generates the AI prompt."""

import os
import time
import argparse
from typing import List, Dict, Optional
from langchain.schema import BaseMessage
from agent.app_ai import AppAI
from agent.app_config import AppConfig
from agent.project_mutator import ProjectMutator

from agent.models import TextBlock
from agent.tags import (
    TAG_BLOCK_BEGIN,
    TAG_BLOCK_END,
    MORE_INSTRUCTIONS,
)
from agent.utils import RefactorMode, Utils
from agent.prompt_utils import PromptUtils


class QuantaAgent:
    """Scans the source code and generates the AI prompt."""

    # Dictionary to store TextBlock objects keyed by 'name'
    blocks: Dict[str, TextBlock] = {}
    # All filen names encountered during the scan, relative to the source folder
    file_names: List[str] = []
    folder_names: List[str] = []

    def __init__(self):
        self.st = None
        self.cfg: argparse.Namespace = AppConfig.get_config(None)
        self.source_folder_len: int = len(self.cfg.source_folder)
        self.ts: str = str(int(time.time() * 1000))
        self.answer: str = ""
        self.mode = RefactorMode.NONE.value
        self.ran: bool = False
        self.prompt: str = ""
        self.system_prompt: str = ""
        self.has_filename_inject = False
        self.has_folder_inject = False
        self.blocks = {}
        # All file names encountered during the scan, relative to the source folder
        self.file_names = []
        self.folder_names = []

    def run(
        self,
        ai_service: str,
        st,
        mode: str,
        output_file_name: str,
        messages: List[BaseMessage],
        input_prompt: str,
        temperature: float,
    ):
        """Runs the agent. We assume that if messages is not `None` then we are in the Streamlit GUI mode, and these messages
        represent the chatbot context. If messages is `None` then we are in the CLI mode, and we will use the `prompt` parameter
        alone without any prior context."""
        self.st = st
        if self.ran:
            Utils.fail_app(
                "Agent has already run. Instantiate a new agent instance to run again.",
                st,
            )
        self.ran = True
        self.prompt = input_prompt
        self.mode = mode

        # default filename to timestamp if empty
        if output_file_name == "":
            output_file_name = self.ts

        # Scan the source folder for files with the specified extensions, to build up the 'blocks' dictionary
        self.scan_directory(self.cfg.source_folder)

        prompt_injects: bool = (
            self.insert_blocks_into_prompt()
            or self.insert_files_and_folders_into_prompt()
        )

        if self.st is not None and prompt_injects:
            self.st.session_state.p_source_provided = True

        if len(self.prompt) > int(self.cfg.max_prompt_length):
            Utils.fail_app(
                f"Prompt length {len(self.prompt)} exceeds the maximum allowed length of {self.cfg.max_prompt_length} characters.",
                st,
            )

        self.build_system_prompt()

        open_ai = AppAI(
            self.cfg,
            self.mode,
            self.system_prompt,
            self.blocks,
            self.st,
        )

        # Need to be sure the current `self.system_prompt`` is in these messages every time we send
        self.answer = open_ai.query(
            ai_service,
            messages,
            self.prompt,
            input_prompt,
            output_file_name,
            self.ts,
            temperature,
        )

        if (
            self.mode == RefactorMode.FILES.value
            or self.mode == RefactorMode.BLOCKS.value
        ):
            ProjectMutator(
                self.st,
                self.mode,
                self.cfg.source_folder,
                self.answer,
                self.ts,
                None,
                self.blocks,
            ).run()

    def build_system_prompt(self):
        """Adds all the instructions to the prompt. This includes instructions for inserting blocks, files,
        folders, and creating files.

        WARNING: This method modifies the `prompt` attribute of the class to have already been configured, and
        also really everything else that this class sets up, so this method should be called last, just before
        the AI query is made.
        """

        self.system_prompt = PromptUtils.get_template(
            "prompt_templates/agent_system_prompt.txt"
        )
        self.system_prompt += MORE_INSTRUCTIONS
        self.add_file_handling_instructions()
        self.add_block_handling_instructions()

    def add_block_handling_instructions(self):
        """Adds instructions for updating blocks. If the prompt contains ${BlockName} tags, then we need to provide
        instructions for how to provide the new block content."""
        if self.mode == RefactorMode.BLOCKS.value and len(self.blocks) > 0:
            self.system_prompt += PromptUtils.get_template(
                "prompt_templates/block_access_instructions.txt"
            )
            if AppConfig.tool_use:
                self.system_prompt += PromptUtils.get_template(
                    "prompt_templates/with_tools/block_update_instructions.txt"
                )
            else:
                self.system_prompt += PromptUtils.get_template(
                    "prompt_templates/without_tools/block_update_instructions.txt"
                )

    def add_file_handling_instructions(self):
        """Adds instructions for inserting files. If the prompt contains ${FileName} or ${FolderName/} tags, then
        we need to provide instructions for how to provide the new file or folder names.
        """
        if self.mode == RefactorMode.FILES.value:
            self.system_prompt += PromptUtils.get_template(
                "prompt_templates/file_access_instructions.txt"
            )
            if AppConfig.tool_use:
                self.system_prompt += PromptUtils.get_template(
                    "prompt_templates/with_tools/file_edit_instructions.txt"
                )
            else:
                self.system_prompt += PromptUtils.get_template(
                    "prompt_templates/without_tools/file_edit_instructions.txt"
                )

    def insert_files_and_folders_into_prompt(self) -> bool:
        """Inserts the file and folder names into the prompt. Prompts can contain ${FileName} and ${FolderName/} tags

        Returns true only if some files or folders were inserted.
        """
        self.prompt, self.has_filename_inject = PromptUtils.insert_files_into_prompt(
            self.prompt, self.cfg.source_folder, self.file_names
        )
        self.prompt, self.has_folder_inject = PromptUtils.insert_folders_into_prompt(
            self.prompt, self.cfg.source_folder, self.folder_names
        )
        return self.has_filename_inject or self.has_folder_inject

    def visit_file(self, path: str):
        """Visits a file and extracts text blocks into `blocks`. So we're just
        scanning the files for the block_begin and block_end tags, and extracting the content between them
        and saving that text for later use
        """

        # get the file name relative to the source folder
        relative_file_name: str = path[self.source_folder_len :]
        self.file_names.append(relative_file_name)

        # Open the file using 'with' which ensures the file is closed after reading
        with Utils.open_file(path) as file:
            block: Optional[TextBlock] = None

            for line in file:  # NOTE: There's no way do to typesafety in loop vars
                # Print each line; using end='' to avoid adding extra newline
                trimmed: str = line.strip()

                if Utils.is_tag_line(trimmed, TAG_BLOCK_BEGIN):
                    name: Optional[str] = Utils.parse_name_from_tag_line(
                        trimmed, TAG_BLOCK_BEGIN
                    )

                    if name in self.blocks:
                        Utils.fail_app(
                            f"Duplicate Block Name {name}. Block Names must be unique across all files.",
                            self.st,
                        )
                    else:
                        # n is a non-optional string
                        n = name if name is not None else ""
                        block = TextBlock(relative_file_name, n, "", False)
                        self.blocks[n] = block
                elif Utils.is_tag_line(trimmed, TAG_BLOCK_END):
                    if block is None:
                        Utils.fail_app(
                            f"""Encountered {TAG_BLOCK_END} without a corresponding {TAG_BLOCK_BEGIN}""",
                            self.st,
                        )
                    block = None
                else:
                    if block is not None:
                        block.content += line

    def scan_directory(self, scan_dir: str):
        """Scans the directory for files with the specified extensions. The purpose of this scan
        is to build up the 'blocks' dictionary with the content of the blocks in the files, and also
        to collect all the filenames into `file_names`
        """

        # Walk through all directories and files in the directory
        for dirpath, _, filenames in os.walk(scan_dir):
            # Get the relative path of the directory, root folder is the source folder and will be "" (empty string) here
            # as the relative path of the source folder is the root folder
            short_dir: str = dirpath[self.source_folder_len :]

            # If not, add it to the set and list
            self.folder_names.append(short_dir)

            for filename in filenames:
                if Utils.should_include_file(AppConfig.ext_set, filename):
                    # build the full path
                    path: str = os.path.join(dirpath, filename)
                    # Call the visitor function for each file
                    self.visit_file(path)

    def insert_blocks_into_prompt(self) -> bool:
        """
        Substitute blocks into the prompt. Prompts can contain ${BlockName} tags, which will be replaced with the
        content of the block with the name 'BlockName'

        Returns true only if someblocks were inserted.
        """
        ret = False
        for key, value in self.blocks.items():
            k = f"block({key})"
            if k in self.prompt:
                ret = True

            self.prompt = self.prompt.replace(
                k,
                f"""
{TAG_BLOCK_BEGIN} {key}
{value.content}
{TAG_BLOCK_END}
""",
            )
        return ret
