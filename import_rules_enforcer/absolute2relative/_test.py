from pathlib import Path
from unittest import TestCase

import libcst

from ._absolute2relative_converter import Absolute2RelativeConverter


class TestAbsolute2RelativeConverter(TestCase):
    def test_converter(self):
        code = """
from .test2 import test
from .test2.test import test
from test_parent_parent.test_parent.test2 import test
from test_parent_parent.test_parent.test2.test import test
from test_parent_parent.test_parent import test
"""
        expected_code = """
from .test2 import test
from .test2.test import test
from .test2 import test
from .test2.test import test
from test_parent_parent.test_parent import test
"""
        module = libcst.parse_module(code)
        updated_module = module.visit(
            Absolute2RelativeConverter(
                Path("test_parent_parent/test_parent/test1.py")
            )
        )
        self.assertEqual(updated_module.code.strip(), expected_code.strip())
