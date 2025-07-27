import re
from collections.abc import Iterable
from collections.abc import Sequence
from itertools import dropwhile
from pathlib import Path

from import_rules_enforcer._access_level_converter import AccessLevelConverter
from libcst import ImportFrom
from libcst import Module


class Private2PublicConverter(AccessLevelConverter):
    def leave_ImportFrom(
        self, original_node: "ImportFrom", updated_node: "ImportFrom"
    ) -> ImportFrom:
        str_import = Module([updated_node]).code
        parts = re.findall(r"from\s+(\S+)", str_import)[0].split(".")
        parts = self._get_relative_parts(parts)
        if len(parts) <= 1:
            return updated_node
        import_source, _ = self._split_import2source_and_elements(str_import)
        imported_file = self._get_import_path(import_source)
        if not imported_file.exists() or not imported_file.name.startswith(
            "_"
        ):
            return updated_node
        joined_parts = ".".join(parts)
        replacement = ".".join(self._remove_last_private(parts))
        new_import = re.sub(
            rf"(from\s+\S*){joined_parts}", rf"\1{replacement}", str_import, 1
        )
        self._check_if_all_defines(new_import)
        return self._str2import(new_import)

    def _get_relative_parts(self, parts: Sequence[str]) -> tuple[str, ...]:
        if parts[0]:
            imported_path = Path("/".join(parts)).absolute()
            parent = self.abs_filepath.parent
            if not imported_path.is_relative_to(parent):
                return ()
            return imported_path.relative_to(parent).parts
        else:
            return tuple(filter(None, parts))

    def _get_absolute_import_path(
        self, parts: Sequence[str]
    ) -> tuple[str, ...]:
        if parts[0]:
            imported_path = Path("/".join(parts)).absolute()
            parent = self.abs_filepath.parent
            return imported_path.relative_to(parent).parts
        else:
            return tuple(filter(None, parts))

    @staticmethod
    def _remove_last_private(parts: Sequence[str]) -> Iterable[str]:
        return reversed(
            tuple(
                dropwhile(
                    lambda part: part.startswith("_") and part in parts,
                    reversed(parts),
                )
            )
        )
