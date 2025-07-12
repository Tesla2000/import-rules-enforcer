import ast
import re
from abc import ABC
from contextlib import suppress
from pathlib import Path
from typing import Optional

import libcst
from import_rules_enforcer._import_converter import ImportConverter
from libcst import Assign
from libcst import CSTVisitor
from libcst import Module
from libcst import Name


class AccessLevelConverter(ImportConverter, ABC):
    def _check_if_all_defines(self, import_path: str) -> None:
        import_source = re.findall(r"from\s+(\S+)", import_path)[0]
        all_elements = self._get_all_elements(import_path)
        needed_elements = self._get_imported_elements(import_path)
        if not all(map(all_elements.__contains__, needed_elements)):
            raise ValueError(
                f"Not all needed elements {needed_elements} are defined in __all__ of {import_source}\n{all_elements}"
            )

    def _get_all_elements(self, import_path: str) -> tuple[str, ...]:
        import_source, elements = re.findall(
            r"from\s+(\S+)\s+import\s+(.+)", import_path
        )[0]
        if import_source.startswith("."):
            import_source = import_source.lstrip(".")
            python_file_path = self.abs_filepath.parent.joinpath(
                import_source.replace(".", "/")
            ).with_suffix(".py")
        else:
            python_file_path = Path(
                import_source.replace(".", "/")
            ).with_suffix(".py")
        python_init_file = python_file_path.parent.joinpath("__init__.py")
        if not python_init_file.exists():
            raise ValueError(f"Init file for {import_path} does not exist")
        return self._extract_all(python_init_file)

    @staticmethod
    def _get_imported_elements(import_path: str) -> tuple[str, ...]:
        elements = re.findall(r"from\s+\S+\s+import\s+(.+)", import_path)[0]
        return tuple(
            elem.split(" as ")[0].strip() for elem in elements.split(",")
        )

    @staticmethod
    def _extract_all(init_file_path: Path) -> tuple[str, ...]:
        all_elements = ()

        class AllExtractor(CSTVisitor):
            def visit_Assign(self, node: "Assign") -> Optional[bool]:
                nonlocal all_elements
                if len(node.targets) != 1:
                    return super().visit_Assign(node)
                name = node.targets[0].target
                if not isinstance(name, Name):
                    return super().visit_Assign(node)
                if name.value != "__all__":
                    return super().visit_Assign(node)
                all_elements = tuple(
                    ast.literal_eval(Module([node.value]).code)
                )
                raise _AllFound()

        content = init_file_path.read_text()
        module = libcst.parse_module(content)
        with suppress(_AllFound):
            module.visit(AllExtractor())
        return all_elements


class _AllFound(Exception):
    pass
