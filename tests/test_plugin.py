from flake8.main import application
from flake8_cgx import CGXTreeChecker


def test_plugin(capsys):
    app = application.Application()
    app.run(["tests/data"])

    captured = capsys.readouterr()

    assert "BLK901 Invalid input." not in captured.out
    assert (
        "tests/data/example.cgx:72:1: F401 'PySide6.QtGui.QAction' imported but unused"
        in captured.out
    )
    assert len(captured.out.splitlines()) == 1


def test_plugin_version():
    assert isinstance(CGXTreeChecker.version, str)
    assert "." in CGXTreeChecker.version


def test_plugin_name():
    assert isinstance(CGXTreeChecker.name, str)
    assert CGXTreeChecker.name == "flake8-cgx"
