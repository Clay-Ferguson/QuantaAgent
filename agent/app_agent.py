"""This is the main agent module that scans the source code and generates the AI prompt."""

import os
import time
from typing import List, Dict
from dataclasses import dataclass
from agent.app_openai import AppOpenAI
from agent.app_config import AppConfig
from agent.file_injection import FileInjection
from agent.tags import (
    TAG_BLOCK_BEGIN,
    TAG_BLOCK_END,
    TAG_BLOCK_INJECT,
    DIVIDER,
)
from agent.utils import Utils
from agent.prompt_templates import PromptTemplates
from langchain.schema import BaseMessage


class QuantaAgent:
    """Scans the source code and generates the AI prompt."""

    @dataclass
    class TextBlock:
        """Represents a block of text in a file."""

        name: str
        content: str

    # Dictionary to store TextBlock objects keyed by 'name'
    blocks: Dict[str, TextBlock] = {}
    # All filen names encountered during the scan, relative to the source folder
    file_names: List[str] = []
    folder_names: List[str] = []

    def __init__(self):
        self.cfg = AppConfig.get_config(None)
        self.source_folder_len = len(self.cfg.source_folder)
        self.ts = str(int(time.time() * 1000))
        self.answer = ""

    def reset(self):
        """Resets the agent's state."""
        self.ts = str(int(time.time() * 1000))
        self.blocks = {}
        # All file names encountered during the scan, relative to the source folder
        self.file_names = []
        self.folder_names = []

    def visit_file(self, path: str):
        """Visits a file and extracts text blocks into `blocks`. So we're just
        scanning the file for the block_begin and block_end tags, and extracting the content between them
        and saving that text for later use
        """
        # print("File:", file_path)

        # Open the file using 'with' which ensures the file is closed after reading
        with open(path, "r", encoding="utf-8") as file:
            block = None

            for line in file:
                # Print each line; using end='' to avoid adding extra newline
                # print(line, end='')
                trimmed = line.strip()

                if Utils.is_tag_line(trimmed, TAG_BLOCK_BEGIN):
                    name = Utils.parse_block_name_from_line(trimmed, TAG_BLOCK_BEGIN)
                    # print(f"Block Name: {name}")
                    if name in self.blocks:
                        Utils.fail_app(f"Duplicate Block Name {name}")
                    else:
                        # print("Creating new block")
                        block = self.TextBlock(name, "")
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
            short_dir = dirpath[self.source_folder_len :]

            # If not, add it to the set and list
            # print(f"Dir: {short_dir}")
            self.folder_names.append(short_dir)

            for filename in filenames:
                # Check the file extension
                _, ext = os.path.splitext(filename)
                if ext.lower() in AppConfig.ext_set:
                    # build the full path
                    path = os.path.join(dirpath, filename)
                    # get the file name relative to the source folder
                    self.file_names.append(path[self.source_folder_len :])
                    # Call the visitor function for each file
                    self.visit_file(path)

    def write_template(self, data_folder: str, output_file_name: str, content: str):
        """Writes the template to a file."""
        filename = f"{data_folder}/{output_file_name}--Q.txt"

        # Write content to the file
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)

    def run(self, st, output_file_name: str, messages: List[BaseMessage], prompt: str):
        """Runs the agent. We assume that if messages is not `None` then we are in the Streamlit GUI mode, and these messages
        represent the chatbot context. If messages is `None` then we are in the CLI mode, and we will use the `prompt` parameter
        alone without any prior context."""
        self.reset()

        # default filename to timestamp if empty
        if output_file_name == "":
            output_file_name = self.ts

        # Scan the source folder for files with the specified extensions, to build up the 'blocks' dictionary
        self.scan_directory(self.cfg.source_folder)

        # Write template before substitutions. This is really essentially a snapshot of what the 'question.txt' file
        # contained when the tool was ran, which is important because users will edit the question.txt file
        # every time they want to ask another AI question, and we want to keep a record of what the question was.
        self.write_template(self.cfg.data_folder, output_file_name, prompt)

        # This divider serves only to give the GUI a way to chop off all these instructions in the display to user
        prompt += DIVIDER
        prompt = self.insert_blocks_into_prompt(prompt)
        prompt = Utils.insert_files_into_prompt(
            prompt, self.cfg.source_folder, self.file_names
        )
        prompt = Utils.insert_folders_into_prompt(
            prompt, self.cfg.source_folder, self.folder_names, AppConfig.ext_set
        )

        # If the prompt has block_inject tags, add instructions for how to provide the
        # new code, in a machine parsable way.
        has_block_inject = Utils.has_tag_lines(prompt, TAG_BLOCK_INJECT)
        if (
            has_block_inject
            and self.cfg.update_strategy == AppConfig.STRATEGY_INJECTION_POINTS
        ):
            prompt += PromptTemplates.get_block_insertion_instructions()

        has_filename_inject = Utils.has_filename_injects(prompt, self.file_names)
        has_folder_inject = Utils.has_folder_injects(prompt, self.folder_names)
        if (
            has_filename_inject
            or has_folder_inject
            and self.cfg.update_strategy == AppConfig.STRATEGY_WHOLE_FILE
        ):
            prompt += PromptTemplates.get_file_insertion_instructions()

        if self.cfg.update_strategy == AppConfig.STRATEGY_WHOLE_FILE:
            prompt += PromptTemplates.get_create_files_instructions()

        if len(prompt) > int(self.cfg.max_prompt_length):
            Utils.fail_app(
                f"Prompt length {len(prompt)} exceeds the maximum allowed length of {self.cfg.max_prompt_length} characters.",
                st,
            )

        open_ai = AppOpenAI(
            self.cfg.openai_api_key,
            self.cfg.openai_model,
            self.cfg.system_prompt,
            self.cfg.data_folder,
        )

        self.answer = open_ai.query(
            messages,
            prompt,
            output_file_name,
            self.ts,
        )

        # Only if set to one of these two strategies, do we ever alter any files
        if (
            self.cfg.update_strategy == AppConfig.STRATEGY_INJECTION_POINTS
            or self.cfg.update_strategy == AppConfig.STRATEGY_WHOLE_FILE
        ):
            FileInjection(
                self.cfg.update_strategy,
                self.cfg.source_folder,
                self.answer,
                self.ts,
                None,
            ).inject()

    def insert_blocks_into_prompt(self, prompt: str):
        """
        Substitute blocks into the prompt. Prompts can contain ${BlockName} tags, which will be replaced with the
        content of the block with the name 'BlockName'
        """
        for key, value in self.blocks.items():
            prompt = prompt.replace(f"${{{key}}}", value.content)
        return prompt
