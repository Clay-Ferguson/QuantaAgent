"""Injects data into files."""

import os
from dataclasses import dataclass
from agent.string_utils import StringUtils
from agent.tags import (
    TAG_BLOCK_INJECT,
    TAG_INJECT_END,
    TAG_INJECT_BEGIN,
)
from agent.utils import Utils


class FileInjection:
    """Injects text blocks into files."""

    blocks = {}

    @dataclass
    class TextBlock:
        """Represents a block of text in a file."""

        name: str
        content: str

    # TODO: need to rename 'content' here to 'ai_answer'
    def __init__(self, source_folder, ext_set, content, ts, suffix):
        self.source_folder = source_folder
        self.source_folder_len = len(source_folder)
        self.ext_set = ext_set
        self.content = content
        self.suffix = suffix
        self.ts = ts

    def inject(self):
        """Injects content into files by extracting all the named blocks on content that are structured like this:

        // inject.begin <Name>
        ...content to be injected...
        // inject.end

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
        defined by '// inject.begin {Name}' and '// inject.end'.

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
            # print(f"Line: [{line}]")

            if Utils.is_tag_line(line, TAG_INJECT_BEGIN):
                # Start of a new block
                current_block_name = Utils.parse_block_name_from_line(
                    line, TAG_INJECT_BEGIN
                )
                # print(f"Found Block: {current_block_name}")
                collecting = True
                current_content = []

            elif Utils.is_tag_line(line, TAG_INJECT_END):
                # print("End of Block")
                # End of the current block
                if current_block_name and collecting:
                    self.blocks[current_block_name] = self.TextBlock(
                        name=current_block_name, content="\n".join(current_content)
                    )
                else:
                    print("No block name or not collecting")
                collecting = False
                current_block_name = None

            elif collecting:
                # Collect the content of the block
                current_content.append(line)

        # print("blocks created: " + str(self.blocks))

    def visit_file(self, filename, ts):
        """Visit the file, to run all injections on the file"""

        # print("Inject Into File:", filename)
        # we need content to be mutable in the methods we pass it to so we hold in a dict
        content = [""]
        try:
            # Read the entire file content
            with open(filename, "r", encoding="utf-8") as file:
                content[0] = file.read()

            modified = False

            # Check if we have a diff for this file
            # TODO: During the initial scan we should've recorded whether each given file was using
            # Injection Points or Whole File Replacement. This way this logic here can be more efficient
            rel_filename = filename[self.source_folder_len :]
            new_content = self.parse_modified_file(self.content, rel_filename)
            if new_content is not None:
                content[0] = new_content
                modified = True
            # else if no new content, so we try any injections
            else:
                # Perform all injections but keep the 'block.inject' lines
                for name, block in self.blocks.items():
                    if self.process_replacements(content, block, name, ts):
                        modified = True

            if modified:
                print("File: " + filename + "\nFinal Content: " + content[0])

            # Write the modified content back to the file
            if modified:
                out_file = (
                    StringUtils.add_filename_suffix(filename, self.suffix)
                    if self.suffix
                    else filename
                )
                with open(out_file, "w", encoding="utf-8") as file:
                    file.write(content[0])

        except FileNotFoundError:
            print(f"The file {filename} does not exist.")
        except IOError:
            print("An error occurred while reading or writing to the file.")

    def parse_modified_file(self, ai_answer, rel_filename):
        """Extract the new content for the given file from the AI answer."""
        if f"""file_begin {rel_filename}""" not in ai_answer:
            print(f"file_begin not found in ai response: {ai_answer}")
            return

        # Scan all the lines in content one by one and extract the new content
        new_content = []
        started = False
        for line in ai_answer.splitlines():
            if started:
                if Utils.is_tag_line(line, "file_end"):
                    break
                new_content.append(line)
            # TODO: this can be a little cleaner because its ugly to cram the filename into the tag, but this will work
            elif Utils.is_tag_line(line, f"file_begin {rel_filename}"):
                if len(new_content) > 0:
                    print(
                        f"Error: file_begin {rel_filename} exists multiple times in ai response. The LLM itself is failing."
                    )
                    exit(1)
                started = True

        if len(new_content) == 0:
            return None

        ret = "\n".join(new_content)
        return ret

    def process_replacements(self, content, block, name, ts):
        """Process the replacements for the given block."""

        # print("replacing: name=" + name)
        # Optimization to avoid unnessary cycles
        if f" {TAG_BLOCK_INJECT} {name}" not in content[0]:
            # print("Skipping: " + name)
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

        We replace the first element of the dict content with the new content, so we're treating 'content'
        as a mutable object.
        """

        found = False
        find = f"{comment_prefix} {TAG_BLOCK_INJECT} {name}"

        if find in content[0]:
            found = True
            content[0] = content[0].replace(
                find,
                f"""{find}
{comment_prefix} {TAG_INJECT_BEGIN} {ts}
{block.content}
{comment_prefix} {TAG_INJECT_END}""",
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
