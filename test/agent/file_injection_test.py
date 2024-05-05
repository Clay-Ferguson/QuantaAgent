"""Test the file injection module."""

import re
from agent.file_injection import FileInjection
from agent.app_config import AppConfig


def test_simple_injection():
    """Run a self-test."""
    inst = FileInjection()
    inst.inject(
        "test",
        ["md"],
        """
ignore 1
block.inject.begin UserAccount.Properties
This is some test content (a).
block.inject.end
ignore 2
block.inject.begin TestB
This is some test content (b).
block.inject.end
ignore 3
""",
        "faketimestamp",
    )
    cfg = AppConfig.get_config()
    ext_list = re.split(r"\s*,\s*", cfg.scan_extensions)
    ext_set = set(ext_list)
    inst.scan_directory(cfg.source_folder, ext_set, "faketimestamp")

    # TODO: This isn't a real test yet.
    assert True
