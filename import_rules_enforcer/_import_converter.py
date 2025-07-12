from abc import ABC
from abc import abstractmethod
from pathlib import Path

import libcst
from libcst import CSTTransformer
from libcst import ImportFrom


class ImportConverter(CSTTransformer, ABC):
    def __init__(self, filepath: Path):
        super().__init__()
        self.abs_filepath = filepath.absolute()
        self.was_modified = False

    @abstractmethod
    def leave_ImportFrom(
        self, original_node: "ImportFrom", updated_node: "ImportFrom"
    ) -> ImportFrom:
        pass

    @staticmethod
    def _str2import(import_str: str) -> ImportFrom:
        updated_node = libcst.parse_statement(import_str).body[0]
        assert isinstance(updated_node, ImportFrom)
        return updated_node
