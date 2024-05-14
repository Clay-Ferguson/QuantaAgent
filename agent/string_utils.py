"""String Utilities Module"""


class StringUtils:
    """String Utilities Class"""

    @staticmethod
    def add_filename_suffix(filename: str, suffix: str) -> str:
        """Inject a suffix into a filename."""

        parts = filename.split(".")
        if len(parts) == 1:  # No file extension
            return f"{filename}{suffix}"
        else:
            return f"{'.'.join(parts[:-1])}{suffix}.{parts[-1]}"
