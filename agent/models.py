from dataclasses import dataclass
from typing import Optional


@dataclass
class TextBlock:
    """Represents a block of text in a file."""

    rel_filename: Optional[str]
    name: str
    content: str
    dirty: bool = False
