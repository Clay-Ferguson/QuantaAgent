from dataclasses import dataclass


@dataclass
class TextBlock:
    """Represents a block of text in a file."""

    name: str
    content: str
