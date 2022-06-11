import argparse
import ast
from dataclasses import dataclass
from importlib import metadata
import logging
from pathlib import Path
from typing import ClassVar, Iterable, NamedTuple, Union

from flake8.options.manager import OptionManager

from . import patch  # noqa: F401

LOG = logging.getLogger("flake8.cgx")


class Error(NamedTuple):
    lineno: int
    col: int
    message: str
    type: type


class CGXVisitor(ast.NodeVisitor):
    pass


@dataclass
class CGXTreeChecker:
    name: ClassVar[str] = "flake8-cgx"
    version: ClassVar[str] = metadata.version("flake8-cgx")

    tree: Union[ast.Module, None] = None
    filename: str = "(none)"
    options: Union[argparse.Namespace, None] = None

    def run(self) -> Iterable[Error]:
        path = Path(self.filename)
        if path.suffix == ".cgx":
            visitor = CGXVisitor(filename=path)
            for error in visitor.run(self.tree):
                yield error

    @classmethod
    def add_options(cls, parser: OptionManager) -> None:
        """This is brittle, there's multiple levels of caching of defaults."""
        if isinstance(parser.parser, argparse.ArgumentParser):
            values = (parser.parser.get_default("filename") or "").split(",")
            values.append("*.cgx")
            parser.parser.set_defaults(filename=",".join(values))
        else:
            for option in parser.options:
                if option.long_option_name == "--filename":
                    option.default = "*.py,*.cgx"
                    option.option_kwargs["default"] = option.default
                    option.to_optparse().default = option.default
                    parser.parser.defaults[option.dest] = option.default
