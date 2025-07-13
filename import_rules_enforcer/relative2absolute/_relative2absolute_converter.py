import os
import re
from pathlib import Path

from import_rules_enforcer._import_converter import ImportConverter
from libcst import ImportFrom
from libcst import Module


class Relative2AbsoluteConverter(ImportConverter):
    def leave_ImportFrom(
        self, original_node: "ImportFrom", updated_node: "ImportFrom"
    ) -> ImportFrom:
        parent_level = len(updated_node.relative)
        if parent_level < 2:
            return updated_node
        relative_path_origin = self.abs_filepath.parents[parent_level - 1]
        str_import = Module([updated_node]).code
        parts = tuple(
            filter(None, re.findall(r"from\s+(\S+)", str_import)[0].split("."))
        )
        absolute_path = Path(relative_path_origin.joinpath("/".join(parts)))
        absolute_replacement = ".".join(
            absolute_path.relative_to(os.getcwd()).parts
        )
        new_import = re.sub(
            r"from\s+\S+", f"from {absolute_replacement}", str_import, 1
        )
        return self._str2import(new_import)
