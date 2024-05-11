"""This is the main agent module that scans the source code and generates the AI prompt."""

import os
import re
import time
from dataclasses import dataclass
from agent.app_openai import AppOpenAI
from agent.app_config import AppConfig
from agent.file_injection import FileInjection
from agent.tags import (
    TAG_BLOCK_BEGIN,
    TAG_BLOCK_END,
    TAG_BLOCK_INJECT,
    TAG_FILE_BEGIN,
    TAG_FILE_END,
    TAG_NEW_FILE_BEGIN,
    TAG_NEW_FILE_END,
)
from agent.utils import Utils
from agent.prompt_templates import PromptTemplates


class QuantaAgent:
    """Scans the source code and generates the AI prompt."""

    @dataclass
    class TextBlock:
        """Represents a block of text in a file."""

        name: str
        content: str

    # Dictionary to store TextBlock objects keyed by 'name'
    blocks = {}
    # All filen names encountered during the scan, relative to the source folder
    file_names = []
    folder_names = []

    cfg = AppConfig.get_config(None)
    source_folder_len = len(cfg.source_folder)
    ts = str(int(time.time() * 1000))

    def visit_file(self, path):
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

    def scan_directory(self, scan_dir):
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

    def write_template(self, data_folder, output_file_name, content):
        """Writes the template to a file."""
        filename = f"{data_folder}/{output_file_name}--Q.txt"

        # Write content to the file
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)

    def run(self):
        """Runs the agent."""

        # Ask for the output file name. They can enter any filename they want. The result will be that after the tool
        # runs, the output will be in the data folder with the name they provided (both a question file and an answer file)
        output_file_name = input(
            "Enter filename for output (without extension, or path): "
        )

        # default filename to timestamp if empty
        if output_file_name == "":
            output_file_name = self.ts

        # Scan the source folder for files with the specified extensions, to build up the 'blocks' dictionary
        self.scan_directory(self.cfg.source_folder)

        with open(
            f"{self.cfg.data_folder}/question.txt", "r", encoding="utf-8"
        ) as file:
            prompt = file.read()

        # Write template before substitutions. This is really essentially a snapshot of what the 'question.txt' file
        # contained when the tool was ran, which is important because users will edit the question.txt file
        # every time they want to ask another AI question, and we want to keep a record of what the question was.
        self.write_template(self.cfg.data_folder, output_file_name, prompt)

        prompt = self.insert_blocks_into_prompt(prompt)
        prompt = self.insert_files_into_prompt(prompt)
        prompt = self.insert_folders_into_prompt(prompt)
        # print(f"AI Prompt: {prompt}")

        # If the prompt has block_inject tags, add instructions for how to provide the
        # new code, in a machine parsable way.
        has_block_inject = self.has_tag_lines(prompt, TAG_BLOCK_INJECT)
        if (
            has_block_inject
            and self.cfg.update_strategy == AppConfig.STRATEGY_INJECTION_POINTS
        ):
            prompt += PromptTemplates.get_block_insertion_instructions()

        has_filename_inject = self.has_filename_injects(prompt)
        has_folder_inject = self.has_folder_injects(prompt)
        if (
            has_filename_inject
            or has_folder_inject
            and self.cfg.update_strategy == AppConfig.STRATEGY_WHOLE_FILE
        ):
            prompt += PromptTemplates.get_file_insertion_instructions()

        if self.cfg.update_strategy == AppConfig.STRATEGY_WHOLE_FILE:
            prompt += PromptTemplates.get_create_files_instructions()

        answer = AppOpenAI(
            self.cfg.openai_api_key,
            self.cfg.openai_model,
            self.cfg.system_prompt,
            self.cfg.data_folder,
        ).query(
            prompt,
            output_file_name,
            self.ts,
        )

        has_new_files = (
            f"""{TAG_NEW_FILE_BEGIN} /""" in answer
            and f"""{TAG_NEW_FILE_END} /""" in answer
        )

        if (
            self.cfg.update_strategy == AppConfig.STRATEGY_INJECTION_POINTS
            or self.cfg.update_strategy == AppConfig.STRATEGY_WHOLE_FILE
        ):
            if (
                has_block_inject
                or has_filename_inject
                or has_folder_inject
                or has_new_files
            ):
                # If the prompt has block_inject tags, add instructions for how to provide the
                # new code, in a machine parsable way.
                FileInjection(
                    self.cfg.update_strategy,
                    self.cfg.source_folder,
                    AppConfig.ext_set,
                    answer,
                    self.ts,
                    None,
                ).inject()

    def has_filename_injects(self, prompt):
        """Returns True if the prompt has any file content injection."""
        for file_name in self.file_names:
            tag_begin = f"{TAG_FILE_BEGIN} {file_name}"
            tag_end = f"{TAG_FILE_END} {file_name}"
            if tag_begin in prompt and tag_end in prompt:
                return True
        return False

    def has_folder_injects(self, prompt):
        """Returns True if the prompt has any folder content injection."""
        for folder_name in self.folder_names:
            tag = f"${{{folder_name}/}}"
            if tag in prompt:
                print(f"Found folder inject tag: {tag}")
                return True
        return False

    def insert_blocks_into_prompt(self, prompt):
        """
        Substitute blocks into the prompt. Prompts can conatin ${BlockName} tags, which will be replaced with the
        content of the block with the name 'BlockName'
        """
        for key, value in self.blocks.items():
            prompt = prompt.replace(f"${{{key}}}", value.content)
        return prompt

    def insert_files_into_prompt(self, prompt):
        """
        Substitute entire file contents into the prompt. Prompts can contain ${FileName} tags,
        which will be replaced with the content of the file with the name 'FileName'
        """
        for file_name in self.file_names:
            tag = f"${{{file_name}}}"
            if tag in prompt:
                with open(
                    self.cfg.source_folder + file_name, "r", encoding="utf-8"
                ) as file:
                    content = file.read()
                    prompt = prompt.replace(
                        tag, PromptTemplates.get_file_content_block(file_name, content)
                    )

        return prompt

    def insert_folders_into_prompt(self, prompt):
        """
        Substitute entire folder contents into the prompt. Prompts can contain ${FolderName} tags,
        which will be replaced with the content of the files inside the folder
        """
        for folder_name in self.folder_names:
            tag = f"${{{folder_name}/}}"
            # print(f"Checking for folder tag: {tag}")
            if tag in prompt:
                # build the content of the folder (that -1 is removing the trailing slash from the folder name)
                content = self.build_folder_content(
                    self.cfg.source_folder + folder_name
                )
                prompt = prompt.replace(tag, content)

        return prompt

    def build_folder_content(self, folder_path):
        """Builds the content of a folder. Which will contain all the filenames and their content."""
        print(f"Building content for folder: {folder_path}")

        content = f"""Below is the content of the files in the folder named {folder_path} (using {TAG_FILE_BEGIN} and {TAG_FILE_END} tags to delimit the files):
        """
        for dirpath, _, filenames in os.walk(folder_path):
            for filename in filenames:
                # Check the file extension
                _, ext = os.path.splitext(filename)
                if ext.lower() in AppConfig.ext_set:
                    # build the full path
                    path = os.path.join(dirpath, filename)
                    # get the file name relative to the source folder
                    file_name = path[self.source_folder_len :]
                    with open(path, "r", encoding="utf-8") as file:
                        file_content = file.read()
                        content += PromptTemplates.get_file_content_block(
                            file_name, file_content
                        )

        return content

    def has_tag_lines(self, prompt, tag):
        """Checks if the prompt has any block_inject tags."""

        # Note: the 're' module caches compiled regexes, so there's no need to store the compiled regex for reuse.
        pattern = rf"(--|//|#) {re.escape(tag)} "
        return re.search(pattern, prompt) is not None
