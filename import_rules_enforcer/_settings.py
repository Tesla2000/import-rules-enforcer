from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings, cli_parse_args=True):
    pos_args: list[str] = Field(default_factory=list)
    root: Path = Field(default_factory=lambda: Path(os.getcwd()))

    def cli_cmd(self) -> None:
        os.chdir(self.root)
        print(self.model_dump())


def create_settings() -> Optional[Settings]:
    try:
        return Settings()
    except SystemExit as e:
        print(e)
