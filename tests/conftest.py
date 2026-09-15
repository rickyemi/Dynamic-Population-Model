"""Shared pytest fixtures.

Every test runs inside a ``tmp_path`` working directory. The pipelines write workbooks, figures and
export folders next to their inputs by design, so a test that ran in the repository root would
leave artefacts behind and the second run would not start from a clean state.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture()
def workdir(tmp_path, monkeypatch) -> Path:
    """A clean working directory, with the config file ignored for the duration of the test."""
    monkeypatch.chdir(tmp_path)
    # Point DPM_CONFIG at a path that does not exist, so a developer's local config.toml cannot
    # change what the tests do.
    monkeypatch.setenv("DPM_CONFIG", str(tmp_path / "no-such-config.toml"))
    for var in ("DPM_DATA_DIR", "DPM_OUT_DIR", "DPM_AUTHOR", "DPM_PRODUCT"):
        monkeypatch.delenv(var, raising=False)
    return tmp_path
