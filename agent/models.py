from dataclasses import dataclass
from typing import Optional


@dataclass
class TextBlock:
    """Represents a block of text in a file."""

    rel_filename: Optional[str]
    name: str
    content: str
    dirty: bool = False

    # Blocks will remain updateable only if there's no block_off/block_on tags inside the block.
    updateable: bool = True

    #constructor function
    def __init__(self, rel_filename: Optional[str], name: str, content: str, dirty: bool = False, updateable: bool = True):
        self.rel_filename = rel_filename
        self.name = name
        self.content = content
        self.dirty = dirty
        self.updateable = updateable