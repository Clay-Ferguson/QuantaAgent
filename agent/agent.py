if __name__ == "__main__":
    print("Error: This script is meant to be imported, not run directly.")
    raise SystemExit(1)

import os
import config
import re
from app_openai import ai_query
import time

class TextBlock:
    def __init__(self, name, content):
        self.name = name
        self.content = content
    
    def __repr__(self):
        return f"TextBlock(name={self.name}, content={self.content})"

class QuantaAgent:
    blocks = {}
    file_names = []
    cfg = config.get_config()
    source_folder_len = len(cfg.source_folder)
    ts = str(int(time.time() * 1000))

    def visit_file(self, path):
        # print("File:", file_path)
        
        # Open the file using 'with' which ensures the file is closed after reading
        with open(path, 'r') as file:
            block = None

            for line in file:
                # Print each line; using end='' to avoid adding extra newline
                # print(line, end='')

                trimmed = line.strip()
                # different files have different comment syntaxes 
                # (-- is for  SQL, // is for C++/Java/JavaScript, etc.)
                if trimmed.startswith("-- block.begin ") or trimmed.startswith("// block.begin ") or trimmed.startswith("# block.begin "):
                    block = None
                    # remove "-- block.begin " from line (or other comment syntaxes)
                    index = trimmed.find("block.begin ")
                    name = trimmed[index+11:].strip()
                    # print(f"Block Name: {name}")
                    if (name in self.blocks):
                        # print("Found existing block")
                        block = self.blocks[name]
                    else:
                        # print("Creating new block")
                        block = TextBlock(name, "")
                        self.blocks[name] = block
                elif trimmed.startswith("-- block.end") or trimmed.startswith("// block.end") or trimmed.startswith("# block.end"):
                    block = None
                else:
                    if block is not None:
                        block.content += line
                
    def scan_directory(self, dir, extensions):
        # extensions should be a set for faster lookup
        extensions = set(extensions)

        # Walk through all directories and files in the directory
        for dirpath, dirnames, filenames in os.walk(dir):
            for filename in filenames:
                # Check the file extension
                _, ext = os.path.splitext(filename)
                if ext.lower() in extensions:
                    # build the full path
                    path = os.path.join(dirpath, filename)
                    self.file_names.append(path[self.source_folder_len:])
                    # Call the visitor function for each file
                    self.visit_file(path)

    def write_template(self, data_folder, ts, content):
        filename = f"{data_folder}/{ts}-question.md"
        
        # Write content to the file
        with open(filename, 'w') as file:
            file.write(content)

    def run(self):
        # Using regex to split and remove spaces
        extensions = re.split(r'\s*,\s*', self.cfg.scan_extensions)
        self.scan_directory(self.cfg.source_folder, extensions)

        # Print all blocks
        # for key, value in blocks.items():
        #    print(f"Block: {key}")
        #    print(f"Content: {value.content}\n"

        with open(f"{self.cfg.data_folder}/question.md", 'r') as file:
            prompt = file.read()

        # Write template before substitutions
        self.write_template(self.cfg.data_folder, self.ts, prompt)

        # Substitute blocks into the prompt
        for key, value in self.blocks.items():
            prompt = prompt.replace(f"${{{key}}}", value.content)

        # Substitute file contents into the prompt
        for file_name in self.file_names:
            tag = f"${{{file_name}}}"
            if tag in prompt:
                with open(self.cfg.source_folder+file_name, 'r') as file:
                    block = file.read()
                    prompt = prompt.replace(tag, block)

        print(f"AI Prompt: {prompt}")

        # ai_query(self.ts, self.cfg.openai_api_key, self.cfg.openai_model, self.cfg.system_prompt, self.cfg.data_folder, prompt)
