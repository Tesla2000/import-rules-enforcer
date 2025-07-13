from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Type

import libcst
from import_rules_enforcer._import_converter import ImportConverter
from import_rules_enforcer._settings import create_settings
from import_rules_enforcer._settings import Settings
from import_rules_enforcer.absolute2relative import Absolute2RelativeConverter
from import_rules_enforcer.private2public import Private2PublicConverter
from import_rules_enforcer.public2private import Public2PrivateConverter
from import_rules_enforcer.relative2absolute import Relative2AbsoluteConverter
from utility_functions import file_modification_transaction


class Main:
    _path2module: dict[Path, libcst.Module]
    _settings: Settings

    def __init__(self):
        self._modified_paths: set[Path] = set()

    def __call__(self) -> int:
        self._settings = create_settings()
        if self._settings is None:
            return 2
        with file_modification_transaction(self._settings.pos_args) as (
            paths,
            contents,
        ):
            self._initialize(paths, contents)
        self._absolute2relative()
        self._relative2absolute()
        self._private2public()
        self._public2private()
        self._modify_files()
        return bool(self._modified_paths)

    def _initialize(
        self, paths: Iterable[Path], contents: Iterable[str]
    ) -> None:
        self._path2module = dict(
            zip(paths, map(libcst.parse_module, contents))
        )

    def _absolute2relative(self) -> None:
        self._convert(Absolute2RelativeConverter)

    def _relative2absolute(self) -> None:
        self._convert(Relative2AbsoluteConverter)

    def _private2public(self) -> None:
        self._convert(Private2PublicConverter)

    def _public2private(self) -> None:
        self._convert(Public2PrivateConverter)

    def _convert(self, converter_type: Type[ImportConverter]) -> None:
        for path, module in self._path2module.items():
            converter_instance = converter_type(path)
            self._path2module[path] = module.visit(converter_instance)
            if converter_instance.was_modified:
                self._modified_paths.add(path)

    def _modify_files(self):
        for filepath in self._modified_paths:
            filepath.write_text(self._path2module[filepath].code)
        if self._modified_paths:
            print(
                "Modified files:\n" + "\n".join(map(str, self._modified_paths))
            )


if __name__ == "__main__":
    Main().__call__()
