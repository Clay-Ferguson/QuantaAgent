"""Tags for the agent module."""

# TODO: Make all use "_" not ".", just so LLM can't confuse with a period (end of sentence)
TAG_BLOCK_BEGIN = "block_begin"
TAG_BLOCK_END = "block_end"
TAG_BLOCK_INJECT = "block_inject"
TAG_INJECT_BEGIN = "inject_begin"
TAG_INJECT_END = "inject_end"

TAG_FILE_BEGIN = "file_begin"
TAG_FILE_END = "file_end"

TAG_INJECT_BEGIN_LEN = len(TAG_INJECT_BEGIN)
TAG_INJECT_END_LEN = len(TAG_INJECT_END)
TAG_BLOCK_BEGIN_LEN = len(TAG_BLOCK_BEGIN)
