"""Unit tests for APP_TARGET specifier parsing.

`_parse_app_target` is pure string logic with several edge cases (path vs.
module ref, optional app name, optional environment), so it is covered here
directly rather than through the subprocess CLI tests.
"""

from __future__ import annotations

import click
import pytest
from cocoindex.cli import _parse_app_target


def test_module_ref_only() -> None:
    assert _parse_app_target("./main.py") == ("./main.py", None, None)
    assert _parse_app_target("mymodule") == ("mymodule", None, None)


def test_app_name_and_env() -> None:
    assert _parse_app_target("./main.py:app2") == ("./main.py", "app2", None)
    assert _parse_app_target("mymodule:my_app@default") == (
        "mymodule",
        "my_app",
        "default",
    )


def test_posix_absolute_path() -> None:
    assert _parse_app_target("/home/u/main.py:app") == ("/home/u/main.py", "app", None)


@pytest.mark.parametrize(
    ("specifier", "expected"),
    [
        (r"C:\projects\myapp\main.py", (r"C:\projects\myapp\main.py", None, None)),
        ("C:/projects/myapp/main.py", ("C:/projects/myapp/main.py", None, None)),
        (r"D:\a\b.py:myapp", (r"D:\a\b.py", "myapp", None)),
        (r"C:\a\b.py:app@prod", (r"C:\a\b.py", "app", "prod")),
    ],
)
def test_windows_drive_letter_is_not_a_separator(
    specifier: str, expected: tuple[str, str | None, str | None]
) -> None:
    assert _parse_app_target(specifier) == expected


def test_single_letter_module_ref_still_splits() -> None:
    """The drive-letter rule requires a path separator, so 'a:app' is unaffected."""
    assert _parse_app_target("a:my_app") == ("a", "my_app", None)


@pytest.mark.parametrize("specifier", ["", ":app", "C:x:y"])
def test_invalid_specifiers(specifier: str) -> None:
    with pytest.raises(click.BadParameter):
        _parse_app_target(specifier)
