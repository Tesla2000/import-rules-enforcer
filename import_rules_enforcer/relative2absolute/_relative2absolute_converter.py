import os

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
        self.was_modified = True
        relative_path_origin = self.abs_filepath.parents[parent_level]
        absolute_replacement = ".".join(
            relative_path_origin.relative_to(os.getcwd()).parts
        )
        new_import = Module([updated_node]).code.replace(
            "." * (parent_level - 1), absolute_replacement, 1
        )
        return self._str2import(new_import)
