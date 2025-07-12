import os
from pathlib import Path
from unittest import TestCase

import libcst

from ._private2public_converter import Private2PublicConverter


class TestPrivate2PublicConverter(TestCase):
    def test_converter(self):
        code = """
from test_parent_parent.test_parent._test import test
from test_parent_parent.test_parent.test._test_module import test
from ._test import test
from .test._test_module import test
"""
        expected_code = """
from test_parent_parent.test_parent._test import test
from test_parent_parent.test_parent.test import test
from ._test import test
from .test import test
"""
        module = libcst.parse_module(code)
        updated_module = module.visit(
            Private2PublicConverter(
                Path("test_parent_parent/test_parent/test.py")
            )
        )
        self.assertEqual(updated_module.code.strip(), expected_code.strip())

    def test_converter_not_all(self):
        code = """
from test_parent_parent.test_parent_not_all._test import test
from test_parent_parent.test_parent.test._test_module import test
from ._test import test
from .test._test_module import test
"""
        module = libcst.parse_module(code)
        with self.assertRaisesRegex(ValueError, " is not in the subpath of "):
            module.visit(
                Private2PublicConverter(
                    Path("test_parent_parent/test_parent/test.py")
                )
            )

    def setUp(self):
        self._cwd = os.getcwd()
        os.chdir(str(Path(__file__).parent))

    def tearDown(self):
        os.chdir(self._cwd)
