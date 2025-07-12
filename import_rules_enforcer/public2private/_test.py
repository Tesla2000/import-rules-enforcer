import os
from pathlib import Path
from unittest import TestCase

import libcst

from ._public2private_converter import Public2PrivateConverter


class TestPublic2PrivateConverter(TestCase):
    def test_converter(self):
        code = """
from . import test
from test import test
from .test import test
from test_parent_parent.test_parent import test
from test_parent_parent.test_parent.test import test
"""
        expected_code = """
from test_parent._test import test
from test_parent._test import test
from .test import test
from test_parent_parent.test_parent import test
from test_parent_parent.test_parent.test import test
"""
        module = libcst.parse_module(code)
        updated_module = module.visit(
            Public2PrivateConverter(
                Path("test_parent_parent/test_parent/test.py")
            )
        )
        self.assertEqual(updated_module.code.strip(), expected_code.strip())

    def setUp(self):
        self._cwd = os.getcwd()
        os.chdir(str(Path(__file__).parent))

    def tearDown(self):
        os.chdir(self._cwd)
