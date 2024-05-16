"""Contains the prompt templates for the agent."""

import os
from typing import List, Optional, Dict
from langchain.prompts import PromptTemplate
from agent.app_config import AppConfig
from agent.string_utils import StringUtils
from agent.tags import (
    TAG_FILE_BEGIN,
    TAG_FILE_END,
    template_info,
)
from agent.utils import Utils


class PromptUtils:
    """Contains the prompt templates for the agent."""

    # Dictionary to store user inputs keyed by id(HumanMessage)
    user_inputs: Dict[int, str] = {}

    tplt_file_content_block: Optional[PromptTemplate] = None

    # caches the version of a template file, after core substitutions have been made from template_info
    template_cache: Dict[str, str] = {}

    @staticmethod
    def get_template(file_name: str) -> str:
        """Get the template for the given file name."""
        if file_name not in PromptUtils.template_cache:
            pt = PromptTemplate.from_file(f"prompt_templates/{file_name}.txt")
            PromptUtils.template_cache[file_name] = (
                "\n\n" + StringUtils.end_slash_remove(pt.format(**template_info))
            )

        return PromptUtils.template_cache[file_name]

    @staticmethod
    def get_file_content_block(file_name: str, content: str) -> str:
        """Get the content block for a file."""
        if PromptUtils.tplt_file_content_block is None:
            PromptUtils.tplt_file_content_block = PromptTemplate.from_file(
                "prompt_templates/file_content_block.txt"
            )
        return "\n\n" + StringUtils.end_slash_remove(
            PromptUtils.tplt_file_content_block.format(
                **template_info, file_name=file_name, content=content
            )
        )

    @staticmethod
    def build_folder_content(folder_path: str, source_folder_len: int) -> str:
        """Builds the content of a folder. Which will contain all the filenames and their content."""
        print(f"Building content for folder: {folder_path}")

        content = f"""

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
            if tag in prompt:
                # build the content of the folder
                content: str = PromptUtils.build_folder_content(
                    source_folder + folder_name,
                    source_folder_len,
                )
                prompt = prompt.replace(tag, content)

        return prompt
