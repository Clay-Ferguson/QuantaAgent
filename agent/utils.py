"""Utilities Module"""

import re


class Utils:
    """Utilities Class"""

    @staticmethod
    def is_tag_line(line, tag):
        """Checks if the line is a line like
        `-- block.begin {Name}` or `// block.begin {Name}` or `# block.begin {Name}`
        or `-- block.end {Name}` or `// block.end {Name}` or `# block.end {Name}`
        """

        # Note: the 're' module caches compiled regexes, so there's no need to store the compiled regex for reuse.
        pattern = rf"^(--|//|#) {re.escape(tag)}"
        return re.search(pattern, line) is not None

    @staticmethod
    def parse_block_name_from_line(line, tag):
        """Parses the block name from the `block.begin` line."""
        index = line.find(f"{tag} ")
        return line[index + len(tag) :].strip()
