import ast
from pathlib import Path
import tokenize
from typing import List

from collagraph.cgx import cgx
from flake8.processor import FileProcessor


build_ast_orig = FileProcessor.build_ast
read_lines_from_filename_orig = FileProcessor.read_lines_from_filename


def build_ast_patched(self) -> ast.AST:
    """Build an abstract syntax tree from the list of lines."""
    tree, _ = cgx.construct_ast(Path(self.filename))
    return tree


def read_lines_from_filename_patched(self) -> List[str]:
    """Read the lines for a file."""
    try:
        parser = cgx.CGXParser()
        parser.feed(Path(self.filename).read_text())

        # Read the data from script block
        script_node = parser.root.child_with_tag("script")
        start, end = script_node.location[0], script_node.end[0] - 1

        with tokenize.open(self.filename) as fh:
            result = fh.readlines()

            actual_result = result[start:end]
            # Prepend some empty (commented) lines to make the errors
            # point out the right location in the cgx file
            actual_result = [
                # prepend with some empty lines
                *(start * ["# noqa\n"]),
                *actual_result,
                # append some more empty lines
                *(9 * ["# noqa\n"]),
            ]

            return actual_result

    except (SyntaxError, UnicodeError):
        # If we can't detect the codec with tokenize.detect_encoding, or
        # the detected encoding is incorrect, just fallback to latin-1.
        with open(self.filename, encoding="latin-1") as fd:
            return fd.readlines()


def build_ast(self):
    if self.filename.endswith(".cgx"):
        return build_ast_patched(self)
    return build_ast_orig(self)


def read_lines_from_filename(self):
    if self.filename.endswith(".cgx"):
        return read_lines_from_filename_patched(self)
    return read_lines_from_filename_orig(self)


# Monkey patch the build_ast function and use collagraph to
# actually build the ast instead
FileProcessor.build_ast = build_ast
FileProcessor.read_lines_from_filename = read_lines_from_filename
