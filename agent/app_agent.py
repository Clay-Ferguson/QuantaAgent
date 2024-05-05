"""This is the main agent module that scans the source code and generates the AI prompt."""

import os
import re
import time
from dataclasses import dataclass

# TODO: VSCode linter is showing these as invalid imports, but they are valid. why?
from app_openai import AppOpenAI
from app_config import AppConfig
from file_injection import FileInjection


class QuantaAgent:
    """Scans the source code and generates the AI prompt."""

    @dataclass
    class TextBlock:
        """Represents a block of text in a file."""

        name: str
        content: str

    blocks = {}
    file_names = []
    cfg = AppConfig.get_config()
    # Using regex to split and remove spaces
    # TODO: need to put ext_list and ext_set inside 'cfg' object.
    ext_list = re.split(r"\s*,\s*", cfg.scan_extensions)
    ext_set = set(ext_list)
    source_folder_len = len(cfg.source_folder)
    ts = str(int(time.time() * 1000))

    def visit_file(self, path):
        """Visits a file and extracts text blocks."""
        # print("File:", file_path)

        # Open the file using 'with' which ensures the file is closed after reading
        with open(path, "r", encoding="utf-8") as file:
            block = None

            for line in file:
                # Print each line; using end='' to avoid adding extra newline
                # print(line, end='')

                trimmed = line.strip()
                # different files have different comment syntaxes
                # (-- is for  SQL, // is for C++/Java/JavaScript, etc.)
                if (
                    trimmed.startswith("-- block.begin ")
                    or trimmed.startswith("// block.begin ")
                    or trimmed.startswith("# block.begin ")
                ):
                    block = None
                    # remove "-- block.begin " from line (or other comment syntaxes)
                    index = trimmed.find("block.begin ")
                    name = trimmed[index + 11 :].strip()
                    # print(f"Block Name: {name}")
                    if name in self.blocks:
                        # print("Found existing block")
                        block = self.blocks[name]
                    else:
                        # print("Creating new block")
                        block = self.TextBlock(name, "")
                        self.blocks[name] = block
                elif (
                    trimmed.startswith("-- block.end")
                    or trimmed.startswith("// block.end")
                    or trimmed.startswith("# block.end")
                ):
                    block = None
                else:
                    if block is not None:
                        block.content += line

    def scan_directory(self, scan_dir):
        """Scans the directory for files with the specified extensions."""

        # Walk through all directories and files in the directory
        for dirpath, _, filenames in os.walk(scan_dir):
            for filename in filenames:
                # Check the file extension
                _, ext = os.path.splitext(filename)
                if ext.lower() in self.ext_set:
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

        output_file_name = input(
            "Enter filename for output (without extension, or path): "
        )

        # default filename to timestamp if empty
        if output_file_name == "":
            output_file_name = self.ts

        self.scan_directory(self.cfg.source_folder)

        # Print all blocks
        # for key, value in blocks.items():
        #    print(f"Block: {key}")
        #    print(f"Content: {value.content}\n"

        with open(f"{self.cfg.data_folder}/question.md", "r", encoding="utf-8") as file:
            prompt = file.read()

        # Write template before substitutions
        self.write_template(self.cfg.data_folder, output_file_name, prompt)

        # Substitute blocks into the prompt
        for key, value in self.blocks.items():
            prompt = prompt.replace(f"${{{key}}}", value.content)

        # Substitute entire file contents into the prompt
        for file_name in self.file_names:
            tag = f"${{{file_name}}}"
            if tag in prompt:
                with open(
                    self.cfg.source_folder + file_name, "r", encoding="utf-8"
                ) as file:
                    block = file.read()
                    prompt = prompt.replace(tag, block)

        # print(f"AI Prompt: {prompt}")

        # If the prompt has block.inject tags, add instructions for how to provide the new code, in a
        # machine parsable way.
        if self.has_block_inject(prompt):
            prompt += self.get_block_insertion_instructions()

        answer = AppOpenAI().query(
            self.cfg.openai_api_key,
            self.cfg.openai_model,
            self.cfg.system_prompt,
            self.cfg.data_folder,
            prompt,
            output_file_name,
            self.ts,
        )

        FileInjection().inject(self.cfg.data_folder, self.ext_set, answer, self.ts)

    # TODO: Need to add explanation that the prefix characters in front of 'block.inject' may vary
    def get_block_insertion_instructions(self):
        """Returns instructions for providing the new code."""

        return """"

To provide me with the new code, use the following strategy: 
Notice that there are sections named `// block.inject {Name}` in the code I gave you. 
I'd like for you to show me just what I need to insert into each of those `block.inject` sections of the code. 
So when you show code, show only the changes and show the changes like this format in your response:

block.inject.begin {Name}
...{SomeContent}...
block.inject.end

You may not need to inject into some of the `block.inject` locations. 
These `block.inject` points are just for you to refer to which places the code needs to be inserted, and to provide it back to me in a machine parsable way.
"""

    def has_block_inject(self, prompt):
        """Checks if the prompt has any block.inject tags."""

        # TODO: AI wrote this line for me, and I can use it elsewhere!
        return re.search(r"(--|//|#) block.inject", prompt) is not None
