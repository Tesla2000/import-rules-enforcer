import ast
from contextlib import suppress
from pathlib import Path
from typing import Optional

import libcst
from libcst import Assign
from libcst import CSTVisitor
from libcst import Module
from libcst import Name


def extract_all(init_file_path: Path) -> tuple[str, ...]:
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
            all_elements = tuple(ast.literal_eval(Module([node.value]).code))
            raise _AllFound()

    content = init_file_path.read_text()
    module = libcst.parse_module(content)
    with suppress(RuntimeError):
        module.visit(AllExtractor())
    return all_elements


class _AllFound(StopIteration):
    pass
