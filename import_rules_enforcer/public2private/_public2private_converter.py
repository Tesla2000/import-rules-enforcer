import re
from collections.abc import Sequence
from pathlib import Path

from libcst import ImportFrom
from libcst import Module

from .._access_level_converter import AccessLevelConverter
from ._get_imports import get_imports


class Public2PrivateConverter(AccessLevelConverter):
    def leave_ImportFrom(
        self, original_node: "ImportFrom", updated_node: "ImportFrom"
    ) -> ImportFrom:
        str_import = Module([updated_node]).code
        parts = re.findall(r"from\s+(\S+)", str_import)[0].split(".")
        if len(parts) > 1 and any(parts):
            return updated_node
        init_path = self.abs_filepath.parent.joinpath("__init__.py")
        imports = get_imports(init_path)
        imported_elements = self._get_imported_elements(str_import)
        if len(imported_elements) > 1:
            raise ValueError("More than one imported elements")
        imported_element = imported_elements[0]
        if imported_element not in imports:
            return updated_node
        import_source = imports[imported_element]
        new_import = re.sub(
            r"from\s+\S+", rf"from {import_source}", str_import, 1
        )
        return self._str2import(new_import)

    def _get_relative_parts(self, parts: Sequence[str]) -> tuple[str, ...]:
        if parts[0]:
            imported_path = Path("/".join(parts)).absolute()
            parent = self.abs_filepath.parent
            return imported_path.relative_to(parent).parts
        else:
            return tuple(filter(None, parts))
