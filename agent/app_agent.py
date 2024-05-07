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
    TAG_INJECT_BEGIN,
    TAG_INJECT_END,
)
from agent.utils import Utils


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

    cfg = AppConfig.get_config(None)
    source_folder_len = len(cfg.source_folder)
    ts = str(int(time.time() * 1000))

    def visit_file(self, path):
        """Visits a file and extracts text blocks into `blocks`. So we're just
        scanning the file for the block.begin and block.end tags, and extracting the content between them
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
                    block = None
                    name = Utils.parse_block_name_from_line(trimmed, TAG_BLOCK_BEGIN)
                    # print(f"Block Name: {name}")
                    if name in self.blocks:
                        # print("Found existing block")
                        block = self.blocks[name]
                    else:
                        # print("Creating new block")
                        block = self.TextBlock(name, "")
                        self.blocks[name] = block
                elif Utils.is_tag_line(trimmed, TAG_BLOCK_END):
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
        # TODO: this scanning logic is in two placesl I think so we can write a reusable function for this
        for dirpath, _, filenames in os.walk(scan_dir):
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
        filename = f"{data_folder}/{output_file_name}--Q.md"

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

        # Print all blocks
        # for key, value in blocks.items():
        #    print(f"Block: {key}")
        #    print(f"Content: {value.content}\n"

        with open(f"{self.cfg.data_folder}/question.md", "r", encoding="utf-8") as file:
            prompt = file.read()

        # Write template before substitutions. This is really essentially a snapshot of what the 'question.md' file
        # contained when the tool was ran, which is important because users will edit the question.md file
        # every time they want to ask another AI question, and we want to keep a record of what the question was.
        self.write_template(self.cfg.data_folder, output_file_name, prompt)

        prompt = self.insert_blocks_into_prompt(prompt)
        prompt = self.insert_files_into_prompt(prompt)

        # print(f"AI Prompt: {prompt}")

        # If the prompt has block.inject tags, add instructions for how to provide the
        # new code, in a machine parsable way.
        has_block_inject = self.has_tag_lines(prompt, TAG_BLOCK_INJECT)
        if (
            has_block_inject
            and self.cfg.update_strategy == AppConfig.STRATEGY_INJECTION_POINTS
        ):
            prompt += self.get_block_insertion_instructions()

        has_filename_inject = self.has_filename_injects(prompt)
        if (
            has_filename_inject
            and self.cfg.update_strategy == AppConfig.STRATEGY_WHOLE_FILE
        ):
            prompt += self.get_file_insertion_instructions()

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

        if (
            # TODO: put these in constants file
            self.cfg.update_strategy == AppConfig.STRATEGY_INJECTION_POINTS
            or self.cfg.update_strategy == AppConfig.STRATEGY_WHOLE_FILE
        ):
            if has_block_inject or has_filename_inject:
                # If the prompt has block.inject tags, add instructions for how to provide the
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
        ### scan all filenames for this pattern: "${filename}" and return True if found"""
        for file_name in self.file_names:
            tag = f"${{{file_name}}}"
            if tag in prompt:
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
                        tag,
                        f"""
file_begin ${{{file_name}}}
{content}
file_end ${{{file_name}}}
""",
                    )

        return prompt

    def get_file_insertion_instructions(self):
        """Returns instructions for providing the new code."""

        return """
If I have sent you individual file(s) and asked you to modify them, in the prompt text above,
then each file is delimited with `file_begin ${FileName}` and `file_end ${FileName}` tags, so you can see what the full content of each file is. 
Note that the actual file content for each file begins on the next line AFTER the `file_begin` line, and ends on the line BEFORE the `file_end` line.

Please provide me with the new version(s) of the file(s) by using the following format:

// file_begin FileName
... the new content of the file ...
// file_end FileName

If you didn't find it necessary to edit a file, you can just omit it from your response. 
If I wasn't asking you to modify any code at all don't include the file_beign or file_end blocks in your response.
"""

    def get_block_insertion_instructions(self):
        """Returns instructions for providing the new code."""

        return f"""

If I was asking you to modify any code, in the prompt above, then to provide me with the new code, use the following strategy: 
Notice that there are sections named `// {TAG_BLOCK_INJECT} {{Name}}` in the code I gave you. 
I'd like for you to show me just what I need to insert into each of those `{TAG_BLOCK_INJECT}` sections of the code. 
So when you show code, show only the changes and show the changes like this format in your response:

// {TAG_INJECT_BEGIN} {{Name}}
... the code to insert ...
// {TAG_INJECT_END} 

Note that the `//` in `// {TAG_BLOCK_INJECT} {{Name}}` is there becasue that example is for Java style comments; however, you may also find 
`-- {TAG_BLOCK_INJECT} {{Name}}` for SQL style comments, or `# {TAG_BLOCK_INJECT} {{Name}}` for Python style comments, and you will handle those also.
You may not need to inject into some of the `{TAG_BLOCK_INJECT}` locations. 
These `{TAG_BLOCK_INJECT}` points are just for you to refer to which places the code needs to be inserted, and to provide it back to me in a machine parsable way.

In the format example above, for the `{TAG_INJECT_BEGIN}` and `{TAG_INJECT_END}` lines, I've given `//` as the comment prefix in the example, 
but you should use whatever comment prefix is appropriate based on the language (or file format) you're working with. 
If there's no comment prefix for the language, just use `//` for the prefix.
"""

    def has_tag_lines(self, prompt, tag):
        """Checks if the prompt has any block.inject tags."""

        # Note: the 're' module caches compiled regexes, so there's no need to store the compiled regex for reuse.
        pattern = rf"(--|//|#) {re.escape(tag)} "
        return re.search(pattern, prompt) is not None
