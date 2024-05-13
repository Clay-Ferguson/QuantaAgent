"""Utilities Module"""

import re
import os
from agent.tags import (
    TAG_INJECT_END,
    TAG_INJECT_BEGIN,
    TAG_FILE_BEGIN,
    TAG_FILE_END,
    TAG_NEW_FILE_BEGIN,
    TAG_NEW_FILE_END,
    DIVIDER,
)


class Utils:
    """Utilities Class"""

    @staticmethod
    def is_tag_and_name_line(line, tag, name):
        """Checks if the line is a line like
        `-- block_begin {Name}` or `// block_begin {Name}` or `# block_begin {Name}`
        or `-- block_end {Name}` or `// block_end {Name}` or `# block_end {Name}`
        """

        # Note: the 're' module caches compiled regexes, so there's no need to store the compiled regex for reuse.
        pattern = rf"^(--|//|#) {re.escape(tag)} {name}"
        return re.search(pattern, line) is not None

    @staticmethod
    def is_tag_line(line, tag):
        """Checks if the line is a line like
        `-- block_begin {Name}` or `// block_begin {Name}` or `# block_begin {Name}`
        or `-- block_end {Name}` or `// block_end {Name}` or `# block_end {Name}`

        Notice that we only check for the tag, not the block name.
        """

        # Note: the 're' module caches compiled regexes, so there's no need to store the compiled regex for reuse.
        pattern = rf"^(--|//|#) {re.escape(tag)}"
        return re.search(pattern, line) is not None

    @staticmethod
    def parse_block_name_from_line(line, tag):
        """Parses the block name from a `... {tag} {name}` formatted line."""
        index = line.find(f"{tag} ")
        return line[index + len(tag) :].strip()

    @staticmethod
    def fail_app(msg):
        """Exits the application with a fail message"""

        print(f"Error: {msg}")
        exit(1)

    @staticmethod
    def ensure_folder_exists(file_path):
        """Ensures that the folder for the file exists."""
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def sanitize_content(content):
        """Makes an AI input or output string presentable in on screen."""

        content = content.split(DIVIDER)[0]

        # Scan all the lines in content one by one and extract the new content
        new_content = []
        started = False
        addendum = []
        for line in content.splitlines():
            if Utils.is_tag_line(line, TAG_FILE_END):
                started = False
                break
            elif Utils.is_tag_line(line, TAG_NEW_FILE_END):
                started = False
                break
            elif Utils.is_tag_line(line, TAG_INJECT_END):
                started = False
                break

            elif Utils.is_tag_line(line, TAG_FILE_BEGIN):
                name = Utils.parse_block_name_from_line(line, TAG_FILE_BEGIN)
                started = True
                new_content.append("File Updated: " + name)

            elif Utils.is_tag_line(line, TAG_NEW_FILE_BEGIN):
                name = Utils.parse_block_name_from_line(line, TAG_NEW_FILE_BEGIN)
                started = True
                new_content.append("File Created: " + name)

            elif Utils.is_tag_line(line, TAG_INJECT_BEGIN):
                name = Utils.parse_block_name_from_line(line, TAG_INJECT_BEGIN)
                started = True
                new_content.append("Code Block Updated: " + name)

            elif started is False:
                new_content.append(line)

        ret = "\n".join(new_content)
        if addendum:
            ret += "\n\n" + "\n".join(addendum)
        return ret
