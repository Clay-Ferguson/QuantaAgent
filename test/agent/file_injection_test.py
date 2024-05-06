"""Test the file injection module."""

from agent.file_injection import FileInjection
from agent.app_config import AppConfig


def test_simple_injection():
    """Run test for simple injection.

    If you run this and you have an injection point named 'UserAccount.Properties' in your source
    files, you should see the injected content in the output, after you run this test.
    """

    cfg = AppConfig.get_config("config/config_test.yaml")
    inst = FileInjection(
        cfg.source_folder,
        AppConfig.ext_set,
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
    assert True
