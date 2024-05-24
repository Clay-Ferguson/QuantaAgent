from typing import List, Dict, Optional

import os
from agent.models import TextBlock
from agent.app_config import AppConfig
from agent.utils import Utils
from agent.tags import TAG_BLOCK_BEGIN, TAG_BLOCK_END


class ProjectLoader:
    # Dictionary to store TextBlock objects keyed by 'name'
    blocks: Dict[str, TextBlock] = {}
    # All filen names encountered during the scan, relative to the source folder
    file_names: List[str] = []
    folder_names: List[str] = []

    def __init__(self, st, source_folder_len: int):
        self.source_folder_len = source_folder_len
        self.st = st

    def reset(self):
        self.blocks = {}
        self.file_names = []
        self.folder_names = []

    def visit_file(self, path: str):
        """Visits a file and extracts text blocks into `blocks`. So we're just
        scanning the files for the block_begin and block_end tags, and extracting the content between them
        and saving that text for later use
        """

        # get the file name relative to the source folder
        relative_file_name: str = path[self.source_folder_len :]
        self.file_names.append(relative_file_name)

        # Open the file using 'with' which ensures the file is closed after reading
        with Utils.open_file(path) as file:
            block: Optional[TextBlock] = None

            for line in file:  # NOTE: There's no way do to typesafety in loop vars
                # Print each line; using end='' to avoid adding extra newline
                trimmed: str = line.strip()

                if Utils.is_tag_line(trimmed, TAG_BLOCK_BEGIN):
                    name: Optional[str] = Utils.parse_name_from_tag_line(
                        trimmed, TAG_BLOCK_BEGIN
                    )

                    if name in self.blocks:
                        Utils.fail_app(
                            f"Duplicate Block Name {name}. Block Names must be unique across all files.",
                            self.st,
                        )
                    else:
                        # n is a non-optional string
                        n = name if name is not None else ""
                        block = TextBlock(relative_file_name, n, "", False)
                        self.blocks[n] = block
                elif Utils.is_tag_line(trimmed, TAG_BLOCK_END):
                    if block is None:
                        Utils.fail_app(
                            f"""Encountered {TAG_BLOCK_END} without a corresponding {TAG_BLOCK_BEGIN}""",
                            self.st,
                        )
                    block = None
                else:
                    if block is not None:
                        block.content += line

    def scan_directory(self, scan_dir: str):
        """Scans the directory for files with the specified extensions. The purpose of this scan
        is to build up the 'blocks' dictionary with the content of the blocks in the files, and also
        to collect all the filenames into `file_names`
        """
        self.reset()
        # Walk through all directories and files in the directory
        for dirpath, _, filenames in os.walk(scan_dir):
            # Get the relative path of the directory, root folder is the source folder and will be "" (empty string) here
            # as the relative path of the source folder is the root folder
            short_dir: str = dirpath[self.source_folder_len :]

            # If not, add it to the set and list
            self.folder_names.append(short_dir)

            for filename in filenames:
                if Utils.should_include_file(AppConfig.ext_set, filename):
                    # build the full path
                    path: str = os.path.join(dirpath, filename)
                    # Call the visitor function for each file
                    self.visit_file(path)
