"""Injects data into files."""

import os
from dataclasses import dataclass
from agent.string_utils import StringUtils


class FileInjection:
    """Injects text blocks into files."""

    blocks = {}

    @dataclass
    class TextBlock:
        """Represents a block of text in a file."""

        name: str
        content: str

    def __init__(self, source_folder, ext_set, content, ts, suffix):
        self.source_folder = source_folder
        self.ext_set = ext_set
        self.content = content
        self.suffix = suffix
        self.ts = ts

    def inject(self):
        """Injects content into files by extracting all the named blocks on content that are structured like this:

        block.inject.begin <Name>
        ...content to be injected...
        block.inject.end

        And inserting into the proper source file injection site identifieid in the code by:
        // block.inject <Name>
        or
        -- block.inject <Name>
        or
        # block.inject <Name>
        """

        self.blocks = {}
        self.parse_injections()
        # print("Injection Blocks: " + str(self.blocks))
        self.scan_directory()

    def parse_injections(self):
        """
        Parses the given multiline string to find and extract blocks of text
        defined by 'block.inject.begin {Name}' and 'block.inject.end'.

        Args:
        text (str): The multiline string containing the text blocks.

        Returns:
        dict: A dictionary where keys are block names and values are TextBlock instances.
        """
        self.blocks = {}
        current_block_name = None
        current_content = []
        collecting = False

        for line in self.content.splitlines():
            line = line.strip()

            if line.startswith("block.inject.begin"):
                # Start of a new block
                current_block_name = (
                    line[len("block.inject.begin") :].strip().strip("{}").strip()
                )
                collecting = True
                current_content = []

            elif line.startswith("block.inject.end"):
                # End of the current block
                if current_block_name and collecting:
                    self.blocks[current_block_name] = self.TextBlock(
                        name=current_block_name, content="\n".join(current_content)
                    )
                collecting = False
                current_block_name = None

            elif collecting:
                # Collect the content of the block
                current_content.append(line)

    def visit_file(self, filename, ts):
        """Visit the file, to run all injections on the file"""

        # print("Inject File:", filename)
        # we need content to be mutable in the methods we pass it to so we hold in a dict
        content = [""]
        try:
            # Read the entire file content
            with open(filename, "r", encoding="utf-8") as file:
                content[0] = file.read()

            found = False
            # Perform all injections but keep the 'block.inject' lines
            for name, block in self.blocks.items():
                if self.process_replacements(content, block, name, ts):
                    found = True

            if found:
                print("File: " + filename + "\nFinal Content: " + content[0])

            # Write the modified content back to the file
            if found:
                out_file = (
                    StringUtils.inject_suffix(filename, self.suffix)
                    if self.suffix
                    else filename
                )
                with open(out_file, "w", encoding="utf-8") as file:
                    file.write(content[0])

        except FileNotFoundError:
            print(f"The file {filename} does not exist.")
        except IOError:
            print("An error occurred while reading or writing to the file.")

    def process_replacements(self, content, block, name, ts):
        """Process the replacements for the given block."""

        # Optimization to avoid unnessary cycles
        if f" block.inject {name}" not in content[0]:
            return False

        # we return true here if we did any replacements
        ret = (
            self.do_replacement("//", content, block, name, ts)
            or self.do_replacement("--", content, block, name, ts)
            or self.do_replacement("#", content, block, name, ts)
        )
        return ret

    def do_replacement(self, comment_prefix, content, block, name, ts):
        """Process the replacement for the given block and comment prefix.

        We replace the first element of the dict content with the new content, so we're treating 'content' as a mutable object.
        """

        found = False
        find = f"{comment_prefix} block.inject {name}"

        if find in content[0]:
            found = True
            content[0] = content[0].replace(
                find,
                f"""{comment_prefix} block.inject {name}
{comment_prefix} inject.begin {ts}
{block.content}
{comment_prefix} inject.end""",
            )
        if found:
            print("Replaced: " + find)
        return found

    def scan_directory(self):
        """Scans the directory for files with the specified extensions."""

        print(f"Doing Injection Scan on: {self.source_folder}")
        # Walk through all directories and files in the directory
        for dirpath, _, filenames in os.walk(self.source_folder):
            for filename in filenames:
                # Check the file extension
                _, ext = os.path.splitext(filename)
                if ext.lower() in self.ext_set:
                    # build the full path
                    path = os.path.join(dirpath, filename)
                    # Call the visitor function for each file
                    self.visit_file(path, self.ts)
