import os
import sys

from import_rules_enforcer import Main
from tests.integration.test_integration import IntegrationBase


class TestIntegrationFirstSet(IntegrationBase):
    set_name: str = "set_1"

    def test_integration(self):
        sys.argv = (
            ["foo.py"]
            + list(
                map(
                    str,
                    map(
                        lambda path: path.relative_to(self.test_dir),
                        self.test_dir.rglob("*.py"),
                    ),
                )
            )
            + ["--root", str(self.test_dir)]
        )

        main_runner = Main()
        assert main_runner()
        os.chdir(self.root)
        self.compare_directories(self.expected_path, self.test_dir)
