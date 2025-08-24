import os
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
        relative_parts = self._get_relative_parts(parts)
        if self._shares_only_project_root(parts):
            pass  # imported file and importing file in different base modules conversion valid
        elif len(relative_parts) == 1:
            return updated_node  # import from private of sibling shouldn't be converted
        elif len(relative_parts) == 0:
            return updated_node
        import_source, _ = self._split_import2source_and_elements(str_import)
        imported_file = self._get_import_path(import_source)
        if not imported_file.exists():
            return updated_node  # import from .venv
        is_private = imported_file.name.startswith("_")
        if not is_private:
            return updated_node  # import not private or from .venv module
        joined_parts = ".".join(parts)
        replacement = ".".join(self._remove_last_private(parts))
        new_import = re.sub(
            rf"(from\s+\S*){joined_parts}", rf"\1{replacement}", str_import, 1
        )
        self._check_if_all_defines(new_import, is_init_child=True)
        return self._str2import(new_import)

    def _get_relative_parts(self, parts: Sequence[str]) -> tuple[str, ...]:
        """Path from parent of the current file"""
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

    def _shares_only_project_root(self, parts: Sequence[str]) -> bool:
        import_root = Path(os.getcwd()).joinpath(parts[0])
        return not self.abs_filepath.is_relative_to(import_root)

    @staticmethod
    def _remove_last_private(parts: Sequence[str]) -> Iterable[str]:
        is_relative = parts and not parts[0]
        if is_relative:
            return parts[:2] + list(
                reversed(
                    tuple(
                        dropwhile(
                            lambda part: part.startswith("_")
                            and part in parts,
                            reversed(parts[2:]),
                        )
                    )
                )
            )  # keeping first elements not to remove everything
        else:
            return reversed(
                tuple(
                    dropwhile(
                        lambda part: part.startswith("_") and part in parts,
                        reversed(parts),
                    )
                )
            )
