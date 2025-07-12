import re
from pathlib import Path

from import_rules_enforcer._import_converter import ImportConverter
from libcst import ImportFrom
from libcst import Module


class Absolute2RelativeConverter(ImportConverter):

    def leave_ImportFrom(
        self, original_node: "ImportFrom", updated_node: "ImportFrom"
    ) -> ImportFrom:
        if updated_node.relative:
            return updated_node
        str_import = Module([updated_node]).code
        path = re.findall(r"from\s+(\S+)", str_import)[0].split(".")
        imported_path = Path("/".join(path)).absolute()
        parent = self.abs_filepath.parent
        parent_is_ancestor = imported_path.is_relative_to(parent)
        parts = imported_path.relative_to(parent).parts
        if not parent_is_ancestor or not parts:
            return updated_node
        replacement = "from ." + ".".join(
            imported_path.relative_to(parent).parts
        )
        new_import = re.sub(r"from\s+\S+", replacement, str_import, 1)
        return self._str2import(new_import)
