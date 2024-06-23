"""This is the main agent module that scans the source code and generates the AI prompt."""

import time
import argparse
from typing import List
from langchain.schema import BaseMessage
from agent.app_ai import AppAI
from agent.app_config import AppConfig
from agent.project_loader import ProjectLoader
from agent.project_mutator import ProjectMutator

from agent.tags import (
    TAG_BLOCK_BEGIN,
    TAG_BLOCK_END,
    MORE_INSTRUCTIONS,
)
from agent.utils import RefactorMode, Utils
from agent.prompt_utils import PromptUtils


class QuantaAgent:
    """Scans the source code and generates the AI prompt."""

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
        self.prj_loader = ProjectLoader(self.st, self.source_folder_len)

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
        self.prj_loader.scan_directory(self.cfg.source_folder)

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
            self.prj_loader.blocks,
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
                self.prj_loader.blocks,
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
        if self.mode == RefactorMode.BLOCKS.value and len(self.prj_loader.blocks) > 0:
            self.system_prompt += PromptUtils.get_template(
                "prompt_templates/block_access_instructions.txt"
            )
            
            self.system_prompt += PromptUtils.get_template(
                "prompt_templates/block_update_instructions.txt"
            )
           

    def add_file_handling_instructions(self):
        """Adds instructions for inserting files. If the prompt contains ${FileName} or ${FolderName/} tags, then
        we need to provide instructions for how to provide the new file or folder names.
        """
        if self.mode == RefactorMode.FILES.value:
            self.system_prompt += PromptUtils.get_template(
                "prompt_templates/file_access_instructions.txt"
            )
            
            self.system_prompt += PromptUtils.get_template(
                "prompt_templates/file_edit_instructions.txt"
            )
           

    def insert_files_and_folders_into_prompt(self) -> bool:
        """Inserts the file and folder names into the prompt. Prompts can contain ${FileName} and ${FolderName/} tags

        Returns true only if some files or folders were inserted.
        """
        self.prompt, self.has_filename_inject = PromptUtils.insert_files_into_prompt(
            self.prompt, self.cfg.source_folder, self.prj_loader.file_names
        )
        self.prompt, self.has_folder_inject = PromptUtils.insert_folders_into_prompt(
            self.prompt, self.cfg.source_folder, self.prj_loader.folder_names
        )
        return self.has_filename_inject or self.has_folder_inject

    def insert_blocks_into_prompt(self) -> bool:
        """
        Substitute blocks into the prompt. Prompts can contain ${BlockName} tags, which will be replaced with the
        content of the block with the name 'BlockName'

        Returns true only if someblocks were inserted.
        """
        ret = False
        for key, value in self.prj_loader.blocks.items():
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
