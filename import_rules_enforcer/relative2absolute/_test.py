from pathlib import Path
from unittest import TestCase

import libcst

from ._relative2absolute_converter import Relative2AbsoluteConverter


class TestRelative2AbsoluteConverter(TestCase):
    def test_converter(self):
        code = """
from ..module import test
from ..module1.module2.module3 import test2
from .module import test2
from .module1.module2.module3 import test2
"""
        expected_code = """from test_parent_parent_parent_parent.test_parent_parent_parent.module import test
from test_parent_parent_parent_parent.test_parent_parent_parent.module1.module2.module3 import test2
from .module import test2
from .module1.module2.module3 import test2
"""
        module = libcst.parse_module(code)
        updated_module = module.visit(
            Relative2AbsoluteConverter(
                Path(
                    "test_parent_parent_parent_parent/test_parent_parent_parent/test_parent_parent/test_parent/test.py"
                )
            )
        )
        self.assertEqual(updated_module.code.strip(), expected_code.strip())
