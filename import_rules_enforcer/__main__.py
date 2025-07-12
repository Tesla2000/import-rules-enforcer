from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Type

import libcst
from import_rules_enforcer.relative2absolute import Relative2AbsoluteConverter
from utility_functions import file_modification_transaction

from ._import_converter import ImportConverter
from ._settings import create_settings
from ._settings import Settings
from .absolute2relative import Absolute2RelativeConverter
from .private2public import Private2PublicConverter
from .public2private import Public2PrivateConverter


class Main:
    _path2module: dict[Path, libcst.Module]
    _settings: Settings
    _modified_paths: set[Path]

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
        if self._modified_paths:
            print(
                "Modified files:\n" + "\n".join(map(str, self._modified_paths))
            )
            return 1
        return 0

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

    def _convert(self, converter: Type[ImportConverter]) -> None:
        for path, module in self._path2module.items():
            converter = converter(path)
            self._path2module[path] = module.visit(converter)
            if converter.was_modified:
                self._modified_paths.add(path)


if __name__ == "__main__":
    Main().__call__()
