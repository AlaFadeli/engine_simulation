import argparse

import pytest

from src.application import Application
from src.cli import (
    build_parser,
    dispatch_command,
    parse_command,
    valid_config_file,
)


@pytest.fixture
def application():
    return Application(
        mode="interactive",
        config_path=None,
    )


def test_default_mode_is_headless():
    parser = build_parser()
    args = parser.parse_args([])

    assert args.mode == "headless"
    assert args.config is None


def test_interactive_mode():
    parser = build_parser()
    args = parser.parse_args(["--interactive"])

    assert args.mode == "interactive"


def test_headless_mode():
    parser = build_parser()
    args = parser.parse_args(["--headless"])

    assert args.mode == "headless"


def test_interactive_and_headless_are_mutually_exclusive():
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["--interactive", "--headless"])


def test_valid_config_file_accepts_existing_file(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text("{}")

    result = valid_config_file(str(config_file))

    assert result == config_file


def test_valid_config_file_rejects_missing_file(tmp_path):
    missing_file = tmp_path / "missing.json"

    with pytest.raises(argparse.ArgumentTypeError):
        valid_config_file(str(missing_file))


def test_empty_command_returns_none():
    assert parse_command("") is None
    assert parse_command("   ") is None


def test_parse_simple_command():
    command, arguments = parse_command("start")

    assert command == "start"
    assert arguments == []


def test_parse_command_is_case_insensitive():
    command, arguments = parse_command("START")

    assert command == "start"
    assert arguments == []


def test_parse_command_preserves_arguments():
    command, arguments = parse_command("throttle 0.75")

    assert command == "throttle"
    assert arguments == ["0.75"]


def test_dispatch_unknown_command_returns_false(application):
    result = dispatch_command("unknown", [], application)

    assert result is False


def test_dispatch_exit_returns_true(application):
    result = dispatch_command("exit", [], application)

    assert result is True


def test_dispatch_quit_returns_true(application):
    result = dispatch_command("quit", [], application)

    assert result is True


def test_dispatch_report_returns_false(application):
    result = dispatch_command("report", [], application)

    assert result is False
