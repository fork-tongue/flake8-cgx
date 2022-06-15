import argparse
import ast
from dataclasses import dataclass
from importlib import metadata
import logging
from typing import ClassVar, Union

from flake8.options.manager import OptionManager

from . import patch  # noqa: F401

LOG = logging.getLogger("flake8.cgx")


@dataclass
class CGXTreeChecker:
    name: ClassVar[str] = "flake8-cgx"
    version: ClassVar[str] = metadata.version("flake8-cgx")

    tree: Union[ast.Module, None] = None
    filename: str = "(none)"
    options: Union[argparse.Namespace, None] = None

    def run(self):
        return
        yield

    @classmethod
    def add_options(cls, parser: OptionManager) -> None:
        """This is brittle, there's multiple levels of caching of defaults."""
        if isinstance(parser.parser, argparse.ArgumentParser):
            values = (parser.parser.get_default("filename") or "").split(",")
            values.append("*.cgx")
            parser.parser.set_defaults(filename=",".join(values))

            # Ignore BLK901 for all cgx files
            values = parser.parser.get_default("per_file_ignores" or "").split(",")
            values.append("*.cgx:BLK901")
            parser.parser.set_defaults(per_file_ignores=",".join(values))
        else:
            for option in parser.options:
                if option.long_option_name == "--filename":
                    option.default = "*.py,*.cgx"
                    option.option_kwargs["default"] = option.default
                    option.to_optparse().default = option.default
                    parser.parser.defaults[option.dest] = option.default
