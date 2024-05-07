"""Test the file injection module."""

import time
from agent.file_injection import FileInjection
from agent.app_config import AppConfig


def test_simple_injection():
    """Run test for simple injection.

    If you run this and you have an injection point named 'UserAccount.Properties' in your source
    files, you should see the injected content in the output, after you run this test.
    """

    ts = str(int(time.time() * 1000))
    cfg = AppConfig.get_config("config/config_test.yaml")
    inst = FileInjection(
        cfg.update_strategy,
        cfg.source_folder,
        AppConfig.ext_set,
        """
# inject.begin InsertTarget
# comment to be inserted
# inject.end
    """,
        ts,
        f"-{ts}",
    )
    inst.inject()
    assert True
