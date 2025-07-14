import re
from functools import lru_cache
from pathlib import Path
from typing import Optional

import libcst
from libcst import CSTVisitor
from libcst import ImportFrom
from libcst import Module


@lru_cache
def get_imports(filepath: Path) -> dict[str, str]:
    if not filepath.exists():
        return {}
    content = filepath.read_text()
    imports = {}

    class ImportGetter(CSTVisitor):
        def visit_ImportFrom(self, node: "ImportFrom") -> Optional[bool]:
            import_path = Module([node]).code
            import_source, elements = re.findall(
                r"from\s+(\S+)\s+import\s+(.+)", import_path
            )[0]
            imports.update(
                (elem.split(" as ")[-1].strip(), import_source)
                for elem in elements.split(",")
            )
            return super().visit_ImportFrom(node)

    libcst.parse_module(content).visit(ImportGetter())
    return imports
