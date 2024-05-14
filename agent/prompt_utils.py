"""Contains the prompt templates for the agent."""

import os
from typing import List, Optional
from langchain.prompts import PromptTemplate
from agent.app_config import AppConfig
from agent.tags import (
    TAG_FILE_BEGIN,
    TAG_FILE_END,
    DIVIDER,
    template_info,
)
from agent.utils import Utils


class PromptUtils:
    """Contains the prompt templates for the agent."""

    # TODO: we'll be moving the two system prompts from the config yaml into this way of handling file-based prompts
    tplt_file_content_block: Optional[PromptTemplate] = None
    tplt_file_insertion_instructions: Optional[PromptTemplate] = None
    tplt_block_insertion_instructions: Optional[PromptTemplate] = None
    tplt_create_files_instructions: Optional[PromptTemplate] = None

    @staticmethod
    def get_file_content_block(file_name: str, content: str) -> str:
        """Returns a file content block for the given file name and content."""
        if PromptUtils.tplt_file_content_block is None:
            PromptUtils.tplt_file_content_block = PromptTemplate.from_file(
                "prompt_templates/file_content_block.txt"
            )
        return "\n\n" + PromptUtils.tplt_file_content_block.format(
            **template_info, file_name=file_name, content=content
        )

    @staticmethod
    def get_file_insertion_instructions() -> str:
        """Returns instructions for providing the new code."""
        if PromptUtils.tplt_file_insertion_instructions is None:
            PromptUtils.tplt_file_insertion_instructions = PromptTemplate.from_file(
                "prompt_templates/file_insertion_instructions.txt"
            )
        return "\n\n" + PromptUtils.tplt_file_insertion_instructions.format(
            **template_info
        )

    @staticmethod
    def get_create_files_instructions() -> str:
        """Returns instructions for creating new files."""
        if PromptUtils.tplt_create_files_instructions is None:
            PromptUtils.tplt_create_files_instructions = PromptTemplate.from_file(
                "prompt_templates/create_files_instructions.txt"
            )
        return "\n\n" + PromptUtils.tplt_create_files_instructions.format(
            **template_info
        )

    @staticmethod
    def get_block_insertion_instructions() -> str:
        """Returns instructions for providing the new code."""
        if PromptUtils.tplt_block_insertion_instructions is None:
            PromptUtils.tplt_block_insertion_instructions = PromptTemplate.from_file(
                "prompt_templates/block_insertion_instructions.txt"
            )
        return "\n\n" + PromptUtils.tplt_block_insertion_instructions.format(
            **template_info
        )

    @staticmethod
    def build_folder_content(folder_path: str, source_folder_len: int) -> str:
        """Builds the content of a folder. Which will contain all the filenames and their content."""
        print(f"Building content for folder: {folder_path}")

        content = f"""{DIVIDER}

Below is the content of the files in the folder named {folder_path} (using {TAG_FILE_BEGIN} and {TAG_FILE_END} tags to delimit the files):
        """
        for dirpath, _, filenames in os.walk(folder_path):
            for filename in filenames:
                # Check the file extension
                if Utils.should_include_file(AppConfig.ext_set, filename):
                    # build the full path
                    path: str = os.path.join(dirpath, filename)
                    # get the file name relative to the source folder
                    file_name: str = path[source_folder_len:]
                    with open(path, "r", encoding="utf-8") as file:
                        file_content = file.read()
                        content += PromptUtils.get_file_content_block(
                            file_name, file_content
                        )

        return content

    @staticmethod
    def insert_files_into_prompt(
        prompt: str, source_folder: str, file_names: List[str]
    ) -> str:
        """
        Substitute entire file contents into the prompt. Prompts can contain ${FileName} tags,
        which will be replaced with the content of the file with the name 'FileName'
        """
        for file_name in file_names:
            tag: str = f"${{{file_name}}}"
            if tag in prompt:
                with open(source_folder + file_name, "r", encoding="utf-8") as file:
                    content: str = file.read()
                    prompt = prompt.replace(
                        tag, PromptUtils.get_file_content_block(file_name, content)
                    )

        return prompt

    @staticmethod
    def insert_folders_into_prompt(
        prompt: str, source_folder: str, folder_names: List[str]
    ) -> str:
        """
        Substitute entire folder contents into the prompt. Prompts can contain ${FolderName} tags,
        which will be replaced with the content of the files inside the folder
        """
        source_folder_len: int = len(source_folder)
        for folder_name in folder_names:
            tag: str = f"${{{folder_name}/}}"
            # print(f"Checking for folder tag: {tag}")
            if tag in prompt:
                # build the content of the folder (that -1 is removing the trailing slash from the folder name)
                content: str = PromptUtils.build_folder_content(
                    source_folder + folder_name,
                    source_folder_len,
                )
                prompt = prompt.replace(tag, content)

        return prompt
