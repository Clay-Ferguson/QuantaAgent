"""Test the file injection module."""

from agent.file_injection import FileInjection
from agent.app_config import AppConfig


def test_simple_injection():
    """Run a self-test."""

    cfg = AppConfig.get_config()
    inst = FileInjection(
        cfg.source_folder,
        cfg.ext_set,
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
        "12345678",
    )
    inst.inject()
    inst.scan_directory()

    # TODO: This isn't a real test yet.
    assert True
