"""The command line surface: help, version, and config precedence.

These are cheap and catch the failures that are embarrassing rather than subtle: a subcommand that
no longer parses, or a config layer that silently ignores what was passed on the command line.
"""
from __future__ import annotations

import pytest

from dpm import cli, config


@pytest.mark.parametrize("command", ["relapse", "tipping-point", "dual-use", "self-test"])
def test_every_subcommand_parses(command):
    args = cli.build_parser().parse_args([command])
    assert args.command == command
    assert callable(args.func)


def test_version_flag_exits_cleanly():
    with pytest.raises(SystemExit) as exc:
        cli.build_parser().parse_args(["--version"])
    assert exc.value.code == 0


def test_command_line_beats_the_config_file(workdir):
    cfg = {"paths": {"data_dir": "from-config"}}
    assert cli._resolve("from-cli", "paths", "data_dir", cfg) == "from-cli"
    assert cli._resolve(None, "paths", "data_dir", cfg) == "from-config"
    assert cli._resolve(None, "paths", "missing", cfg) is None


def test_missing_config_file_is_not_an_error(workdir):
    assert config.load(workdir / "nope.toml") == {}


def test_relative_paths_resolve_against_the_repo_root():
    resolved = config.resolve_dir("data/raw")
    assert resolved.is_absolute() and resolved.name == "raw"
