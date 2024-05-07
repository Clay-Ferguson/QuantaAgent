"""Utilities Module"""

import re


class Utils:
    """Utilities Class"""

    @staticmethod
    def is_tag_and_name_line(line, tag, name):
        """Checks if the line is a line like
        `-- block.begin {Name}` or `// block.begin {Name}` or `# block.begin {Name}`
        or `-- block.end {Name}` or `// block.end {Name}` or `# block.end {Name}`
        """

        # Note: the 're' module caches compiled regexes, so there's no need to store the compiled regex for reuse.
        pattern = rf"^(--|//|#) {re.escape(tag)} {name}"
        return re.search(pattern, line) is not None

    @staticmethod
    def is_tag_line(line, tag):
        """Checks if the line is a line like
        `-- block.begin {Name}` or `// block.begin {Name}` or `# block.begin {Name}`
        or `-- block.end {Name}` or `// block.end {Name}` or `# block.end {Name}`

        Notice that we only check for the tag, not the block name.
        """

        # Note: the 're' module caches compiled regexes, so there's no need to store the compiled regex for reuse.
        pattern = rf"^(--|//|#) {re.escape(tag)}"
        return re.search(pattern, line) is not None

    @staticmethod
    def parse_block_name_from_line(line, tag):
        """Parses the block name from a `// {tag} {name}` formatted line."""
        index = line.find(f"{tag} ")
        return line[index + len(tag) :].strip()
