"""This is the main agent module that scans the source code and generates the AI prompt."""

import os
import time
import argparse
from typing import List, Dict, Optional
from langchain.schema import BaseMessage
from agent.app_openai import AppOpenAI
from agent.app_config import AppConfig
from agent.project_mutator import ProjectMutator

from agent.models import TextBlock
from agent.tags import (
    TAG_BLOCK_BEGIN,
    TAG_BLOCK_END,
    TAG_BLOCK_INJECT,
    MORE_INSTRUCTIONS,
)
from agent.utils import Utils
from agent.prompt_utils import PromptUtils


class QuantaAgent:
    """Scans the source code and generates the AI prompt."""

    # Dictionary to store TextBlock objects keyed by 'name'
    blocks: Dict[str, TextBlock] = {}
    # All filen names encountered during the scan, relative to the source folder
    file_names: List[str] = []
    folder_names: List[str] = []

    def __init__(self):
        self.cfg: argparse.Namespace = AppConfig.get_config(None)
        self.source_folder_len: int = len(self.cfg.source_folder)
        self.ts: str = str(int(time.time() * 1000))
        self.answer: str = ""
        self.update_strategy = AppConfig.STRATEGY_WHOLE_FILE
        self.ran: bool = False
        self.prompt: str = ""
        self.has_filename_inject = False
        self.has_folder_inject = False
        self.blocks = {}
        # All file names encountered during the scan, relative to the source folder
        self.file_names = []
        self.folder_names = []

    def run(
        self,
        st,
        update_strategy: str,
        output_file_name: str,
        messages: Optional[List[BaseMessage]],
        input_prompt: str,
    ):
        """Runs the agent. We assume that if messages is not `None` then we are in the Streamlit GUI mode, and these messages
        represent the chatbot context. If messages is `None` then we are in the CLI mode, and we will use the `prompt` parameter
        alone without any prior context."""
        if self.ran:
            Utils.fail_app(
                "Agent has already run. Instantiate a new agent instance to run again.",
                st,
            )
        self.ran = True
        self.prompt = input_prompt
        self.update_strategy = update_strategy

        # default filename to timestamp if empty
        if output_file_name == "":
            output_file_name = self.ts

        # Scan the source folder for files with the specified extensions, to build up the 'blocks' dictionary
        self.scan_directory(self.cfg.source_folder)

        # Write template before substitutions. This is really essentially a snapshot of what the 'question.txt' file
        # contained when the tool was ran, which is important because users will edit the question.txt file
        # every time they want to ask another AI question, and we want to keep a record of what the question was.
        Utils.write_file(
            f"{self.cfg.data_folder}/{output_file_name}--Q.txt", self.prompt
        )

        self.add_all_prompt_instructions(st)
        system_prompt = PromptUtils.get_template("agent_system_prompt")

        open_ai = AppOpenAI(
            self.cfg.openai_api_key,
            self.cfg.openai_model,
            system_prompt,
            self.cfg.data_folder,
        )

        self.answer = open_ai.query(
            messages,
            self.prompt,
            input_prompt,
            output_file_name,
            self.ts,
        )

        # Only if set to one of these two strategies, do we ever alter any files
        if (
            self.update_strategy == AppConfig.STRATEGY_INJECTION_POINTS
            or self.update_strategy == AppConfig.STRATEGY_WHOLE_FILE
            or self.update_strategy == AppConfig.STRATEGY_BLOCKS
        ):
            ProjectMutator(
                self.update_strategy,
                self.cfg.source_folder,
                self.answer,
                self.ts,
                None,
            ).run()

    def add_all_prompt_instructions(self, st):
        """Adds all the instructions to the prompt. This includes instructions for inserting blocks, files,
        folders, and creating files."""
        self.prompt += MORE_INSTRUCTIONS
        self.insert_blocks_into_prompt()
        self.insert_files_and_folders_into_prompt()

        # TODO: These insertion instructions should be moved to the SystemPrompt,so they're not repeated in every prompt
        self.add_block_insertion_instructions()
        self.add_file_insertion_instructions()
        self.add_create_file_instructions()
        self.add_block_update_instructions()

        if len(self.prompt) > int(self.cfg.max_prompt_length):
            Utils.fail_app(
                f"Prompt length {len(self.prompt)} exceeds the maximum allowed length of {self.cfg.max_prompt_length} characters.",
                st,
            )

    def add_block_update_instructions(self):
        """Adds instructions for updating blocks. If the prompt contains ${BlockName} tags, then we need to provide
        instructions for how to provide the new block content."""
        if self.update_strategy == AppConfig.STRATEGY_BLOCKS and len(self.blocks) > 0:
            self.prompt += PromptUtils.get_template("block_update_instructions")

    def add_create_file_instructions(self):
        """Adds instructions for creating files. If the update strategy is 'whole_file', then we need to
        provide instructions for how to create files."""
        if self.update_strategy == AppConfig.STRATEGY_WHOLE_FILE:
            self.prompt += PromptUtils.get_template("create_files_instructions")

    def add_file_insertion_instructions(self):
        """Adds instructions for inserting files. If the prompt contains ${FileName} or ${FolderName/} tags, then
        we need to provide instructions for how to provide the new file or folder names.
        """
        if (
            self.has_filename_inject
            or self.has_folder_inject
            and self.update_strategy == AppConfig.STRATEGY_WHOLE_FILE
        ):
            self.prompt += PromptUtils.get_template("file_insertion_instructions")

    def add_block_insertion_instructions(self):
        """Adds instructions for inserting blocks. If the prompt contains ${BlockName} tags, then we need to provide
        instructions for how to provide the new block content."""
        # If the prompt has block_inject tags, add instructions for how to provide the
        # new code, in a machine parsable way.
        has_block_inject: bool = Utils.has_tag_lines(self.prompt, TAG_BLOCK_INJECT)
        if (
            has_block_inject
            and self.update_strategy == AppConfig.STRATEGY_INJECTION_POINTS
        ):
            self.prompt += PromptUtils.get_template("block_insertion_instructions")

    def insert_files_and_folders_into_prompt(self):
        """Inserts the file and folder names into the prompt. Prompts can contain ${FileName} and ${FolderName/} tags"""
        self.prompt, self.has_filename_inject = PromptUtils.insert_files_into_prompt(
            self.prompt, self.cfg.source_folder, self.file_names
        )
        self.prompt, self.has_folder_inject = PromptUtils.insert_folders_into_prompt(
            self.prompt, self.cfg.source_folder, self.folder_names
        )

    def visit_file(self, path: str):
        """Visits a file and extracts text blocks into `blocks`. So we're just
        scanning the files for the block_begin and block_end tags, and extracting the content between them
        and saving that text for later use
        """

        # Open the file using 'with' which ensures the file is closed after reading
        with Utils.open_file(path) as file:
            block: Optional[TextBlock] = None

            for line in file:  # NOTE: There's no way do to typesafety in loop vars
                # Print each line; using end='' to avoid adding extra newline
                trimmed: str = line.strip()

                if Utils.is_tag_line(trimmed, TAG_BLOCK_BEGIN):
                    name: str = Utils.parse_block_name_from_line(
                        trimmed, TAG_BLOCK_BEGIN
                    )
                    if name in self.blocks:
                        Utils.fail_app(f"Duplicate Block Name {name}")
                    else:
                        block = TextBlock(name, "")
                        self.blocks[name] = block
                elif Utils.is_tag_line(trimmed, TAG_BLOCK_END):
                    if block is None:
                        Utils.fail_app(
                            f"""Encountered {TAG_BLOCK_END} without a corresponding {TAG_BLOCK_BEGIN}"""
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
                    # get the file name relative to the source folder
                    self.file_names.append(path[self.source_folder_len :])
                    # Call the visitor function for each file
                    self.visit_file(path)

    def insert_blocks_into_prompt(self):
        """
        Substitute blocks into the prompt. Prompts can contain ${BlockName} tags, which will be replaced with the
        content of the block with the name 'BlockName'
        """
        for key, value in self.blocks.items():
            self.prompt = self.prompt.replace(f"${{{key}}}", value.content)
