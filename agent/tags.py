"""Tags for the agent module."""

from typing import Dict

MORE_INSTRUCTIONS = "\n----\nAdditional Instructions:\n"

# block_begin/end are used like this in source code projects:
#     // block_begin: block_name
# and are also used in the responses from the LLM to indicate blocks of code
# but the LLM responses don't start with comment characters.
TAG_BLOCK_BEGIN = "block_begin"
TAG_BLOCK_END = "block_end"

TAG_BLOCK_INJECT = "block_inject"

# NOTE: block_begin/end blocks can CONTAIN inject_begin/end blocks so don't try to simplify this
# by just using block_begin/end blocks because that won't work
TAG_INJECT_BEGIN = "inject_begin"
TAG_INJECT_END = "inject_end"

TAG_FILE_BEGIN = "file_begin"
TAG_FILE_END = "file_end"

TAG_NEW_FILE_BEGIN = "new_file_begin"
TAG_NEW_FILE_END = "new_file_end"

TAG_INJECT_BEGIN_LEN = len(TAG_INJECT_BEGIN)
TAG_INJECT_END_LEN = len(TAG_INJECT_END)
TAG_BLOCK_BEGIN_LEN = len(TAG_BLOCK_BEGIN)

template_info: Dict[str, str] = {
    "TAG_BLOCK_INJECT": f"""{TAG_BLOCK_INJECT}""",
    "TAG_BLOCK_BEGIN": f"""{TAG_BLOCK_BEGIN}""",
    "TAG_BLOCK_END": f"""{TAG_BLOCK_END}""",
    "TAG_INJECT_BEGIN": f"""{TAG_INJECT_BEGIN}""",
    "TAG_INJECT_END": f"""{TAG_INJECT_END}""",
    "TAG_FILE_BEGIN": f"""{TAG_FILE_BEGIN}""",
    "TAG_FILE_END": f"""{TAG_FILE_END}""",
    "TAG_NEW_FILE_BEGIN": f"""{TAG_NEW_FILE_BEGIN}""",
    "TAG_NEW_FILE_END": f"""{TAG_NEW_FILE_END}""",
}
