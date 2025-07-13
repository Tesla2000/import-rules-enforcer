from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import CliPositionalArg


class Settings(BaseSettings, cli_parse_args=True):
    pos_args: CliPositionalArg[list[str]] = Field(default_factory=list)
    root: Path = Field(default_factory=lambda: Path(os.getcwd()))


def create_settings() -> Optional[Settings]:
    try:
        setting = Settings()
        os.chdir(setting.root)
        return setting
    except SystemExit as e:
        print(e)
