"""Runtime configuration: defaults, an optional TOML file, and environment overrides.

Why this exists. Each pipeline module carries its own defaults so the notebooks run unchanged, but
those defaults are local Windows paths belonging to whoever wrote them. Committing a path with a
user name in it and expecting the next person to edit the source is how a repository acquires merge
conflicts in the first cell. Precedence, lowest to highest:

    module defaults  <  config/config.toml  <  DPM_* environment variables  <  command line

TOML is read with ``tomllib`` from the standard library, so this adds no dependency. The file is
optional: with no ``config/config.toml`` present, everything falls through to the module defaults
and the pipelines behave exactly as the notebooks do.
"""
from __future__ import annotations

import os
import tomllib
from pathlib import Path

# repo root = .../src/dpm/config.py -> parents[2]
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "config" / "config.toml"
EXAMPLE_CONFIG = ROOT / "config" / "config.example.toml"

# Environment variable -> (section, key) in the TOML file
ENV_MAP = {
    "DPM_DATA_DIR": ("paths", "data_dir"),
    "DPM_OUT_DIR": ("paths", "out_dir"),
    "DPM_AUTHOR": ("run", "author"),
    "DPM_PRODUCT": ("run", "product"),
}


def config_path() -> Path:
    """The config file in use. ``DPM_CONFIG`` overrides the default location."""
    return Path(os.environ.get("DPM_CONFIG", DEFAULT_CONFIG))


def load(path=None) -> dict:
    """Read the config file if it exists, then apply environment overrides.

    A missing file is not an error: the pipelines have working defaults, and requiring a config
    file to run a self test would make the repository harder to try than it needs to be.
    """
    path = Path(path) if path else config_path()
    data: dict = {}
    if path.exists():
        with path.open("rb") as fh:
            data = tomllib.load(fh)

    for env, (section, key) in ENV_MAP.items():
        value = os.environ.get(env)
        if value:
            data.setdefault(section, {})[key] = value
    return data


def get(section: str, key: str, default=None, cfg: dict | None = None):
    """One value, or ``default`` when neither the file nor the environment supplies it."""
    cfg = load() if cfg is None else cfg
    return cfg.get(section, {}).get(key, default)


def resolve_dir(value, fallback=None) -> Path | None:
    """Expand ``~`` and make a relative path relative to the repository root, not the cwd."""
    value = value or fallback
    if not value:
        return None
    path = Path(str(value)).expanduser()
    return path if path.is_absolute() else (ROOT / path).resolve()
