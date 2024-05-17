"""String Utilities Module"""


class StringUtils:
    """String Utilities Class"""

    @staticmethod
    def post_process_template(prompt: str) -> str:
        """Remove the ending slash from lines.
        And remove all lines in the prompt that start with `-- ` because they are comments.
        """

        # Removes the commented lines from the prompt (lines that start with '-- ')
        prompt = "\n".join(
            [line.rstrip() for line in prompt.split("\n") if not line.startswith("-- ")]
        )

        return prompt.replace("\\\n", "")

    @staticmethod
    def add_filename_suffix(filename: str, suffix: str) -> str:
        """Inject a suffix into a filename."""

        parts = filename.split(".")
        if len(parts) == 1:  # No file extension
            return f"{filename}{suffix}"
        else:
            return f"{'.'.join(parts[:-1])}{suffix}.{parts[-1]}"
