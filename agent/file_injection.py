"""Injects data into files."""

import os
from dataclasses import dataclass


class FileInjection:
    """Injects text blocks into files."""

    blocks = {}

    @dataclass
    class TextBlock:
        """Represents a block of text in a file."""

        name: str
        content: str

    # TODO: pass all these args into a constructor and don't pass around all methods.
    def inject(self, source_folder, ext_set, content, ts):
        """Injects content info files by extracting all the named blocks on content that are structured like this:

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

        self.parse_injections(content)
        # print("Injection Blocks: " + str(self.blocks))
        self.scan_directory(source_folder, ext_set, ts)

    def parse_injections(self, text):
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

        for line in text.splitlines():
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
                with open(filename, "w", encoding="utf-8") as file:
                    file.write(content[0])

        except FileNotFoundError:
            print(f"The file {filename} does not exist.")
        except IOError:
            print("An error occurred while reading or writing to the file.")

    def process_replacements(self, content, block, name, ts):
        """Process the replacements for the given block."""

        # we return true here if we did any replacements
        ret = (
            self.do_replacement("//", content, block, name, ts)
            or self.do_replacement("--", content, block, name, ts)
            or self.do_replacement("#", content, block, name, ts)
        )
        return ret

    def do_replacement(self, comment_prefix, content, block, name, ts):
        """Process the replacement for the given block and comment prefix."""
        found = False
        find = f"{comment_prefix} block.inject {name}"

        if find in content[0]:
            found = True
            content[0] = content[0].replace(
                find,
                f"""
{comment_prefix} block.inject {name}
{comment_prefix} inject.begin {ts}
{block.content}
{comment_prefix} inject.end
""",
            )
        if found:
            print("Replaced: " + find)
        return found

    def scan_directory(self, scan_dir, ext_set, ts):
        """Scans the directory for files with the specified extensions."""

        print(f"Doing Injection Scan on: {scan_dir}")
        # Walk through all directories and files in the directory
        for dirpath, _, filenames in os.walk(scan_dir):
            for filename in filenames:
                # Check the file extension
                _, ext = os.path.splitext(filename)
                if ext.lower() in ext_set:
                    # build the full path
                    path = os.path.join(dirpath, filename)
                    # Call the visitor function for each file
                    self.visit_file(path, ts)
