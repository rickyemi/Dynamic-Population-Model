#!/usr/bin/env python3
"""Generate the ``src/dpm/*.py`` modules from the notebooks in ``notebooks/``.

Why generate rather than maintain two copies: the notebooks are the reviewed, executable record of
each pipeline, and a hand-typed module would drift from them within one change. Each markdown cell
becomes the comment block above the code it documented, so the rationale travels with the code.

What the converter has to change, and why:

* **Imports are merged into one block at the top.** A notebook repeats them per workflow so each
  half can be run alone; a module imports once.
* **Cells that execute a run are dropped** and replaced by the footer in ``tools/footers/``. A
  module must not do work on import: importing it for a single helper would otherwise rebuild
  every workbook in the configured folder.
* **Configuration cells are collected into one CONFIGURATION section** so every default sits in one
  place and can be overridden by ``config/config.toml`` or on the command line.
* **``display()`` becomes ``print()``** where the footer needs it, since ``display`` is an IPython
  builtin that does not exist outside a notebook.

Usage:  python tools/nb_to_module.py [--check]

``--check`` regenerates into a temporary folder and compares, so CI can fail a commit where the
module and its notebook have diverged.
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
import textwrap
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[1]
NB_DIR = ROOT / "notebooks"
OUT_DIR = ROOT / "src" / "dpm"
FOOTER_DIR = Path(__file__).resolve().parent / "footers"

BANNER = "# " + "=" * 96

# Shared import block. Every module gets the same one; unused imports in a given module are
# harmless and keep the three files consistent to read.
IMPORTS = """from __future__ import annotations

import argparse
import getpass
import platform
import re
import shutil
import sys
import textwrap
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
"""

SPECS = {
    "relapse_popextrapolation": {
        "notebook": "01_relapse_calculation_and_popextrapolation.ipynb",
        "title": "Relapse calculation and population extrapolation",
        "extra_imports": [
            "from openpyxl import load_workbook",
            "from openpyxl.formatting.rule import FormulaRule",
            "from openpyxl.styles import Alignment, Border, Font, PatternFill, Side",
            "from openpyxl.utils import get_column_letter",
        ],
        # cell index -> how to treat it
        "constants": [2, 23],       # imports plus constants; the imports are stripped
        "config": [4, 25],
        "drop": [18, 19, 55, 56],   # run cells, replaced by the footer
        "split": {21: "w1_mock_dir = ", 58: "w2_mock_dir = "},
    },
    "tipping_point_plotting": {
        "notebook": "02_tipping_point_1d_plotting.ipynb",
        "title": "Tipping point 1D plotting",
        "extra_imports": [
            "import matplotlib",
            'matplotlib.use("Agg")   # write files without needing a display',
            "import matplotlib.pyplot as plt",
            "from matplotlib.backends.backend_pdf import PdfPages",
            "from matplotlib.lines import Line2D",
        ],
        "constants": [2],
        "config": [4],
        "drop": [23, 24, 28],
        "split": {26: "export_dir = export_outputs("},
    },
    "dual_use_optimizer": {
        "notebook": "03_dual_use_calculation_optimizer.ipynb",
        "title": "Dual use calculation optimizer",
        "extra_imports": [
            "from openpyxl import Workbook, load_workbook",
            "from openpyxl.styles import Alignment, Border, Font, PatternFill, Side",
            "from openpyxl.utils import get_column_letter as L",
        ],
        "constants": [3],
        "config": [5],
        "drop": [18, 21],
        "split": {17: "result = run_pipeline()", 20: "report = validate_against_source("},
    },
}


def md_to_comment(source: str) -> str:
    """Turn a markdown cell into a comment block, keeping tables and lists legible."""
    lines: list[str] = []
    for raw in source.strip().split("\n"):
        line = raw.rstrip()
        if line.startswith("---"):
            continue
        if line.startswith("#"):
            lines += ["", BANNER, f"# {line.lstrip('#').strip().upper()}", BANNER]
            continue
        if not line:
            lines.append("#")
            continue
        if line.startswith(("|", "```", "*", "-", "  ")) or re.match(r"^\d+\.", line):
            lines.append("# " + line)
        else:
            lines += ["# " + w for w in textwrap.wrap(line, 94)]
    return "\n".join(lines)


def strip_imports(source: str) -> str:
    """Drop the pip hint and the import block from a constants cell, keep everything after."""
    body = source
    for anchor in ("from openpyxl.utils import get_column_letter as L",
                   "from openpyxl.utils import get_column_letter",
                   "from matplotlib.lines import Line2D",
                   "import pandas as pd"):
        if anchor in body:
            body = body.split(anchor, 1)[1]
            break
    return body.lstrip("\n")


def build_module(name: str, spec: dict) -> str:
    nb = nbformat.read(NB_DIR / spec["notebook"], as_version=4)
    cells = nb.cells
    split_defs: dict[int, str] = {}
    split_runs: dict[int, str] = {}

    header_doc = (FOOTER_DIR / f"{name}.docstring.txt").read_text(encoding="utf-8").rstrip()
    parts = ['#!/usr/bin/env python3', f'"""{header_doc}\n"""',
             IMPORTS + "\n".join(spec["extra_imports"]),
             'pd.set_option("display.width", 220)\npd.set_option("display.max_columns", 40)']

    config_blocks = []
    for i, cell in enumerate(cells):
        if cell.cell_type == "markdown":
            text = md_to_comment(cell.source)
            if text.strip():
                parts.append(text)
            continue

        src = cell.source.rstrip()
        if i in spec["config"]:
            config_blocks.append(src)
            continue
        if i in spec["drop"]:
            continue
        if i in spec["split"]:
            marker = spec["split"][i]
            idx = src.index(marker)
            split_defs[i], split_runs[i] = src[:idx].rstrip(), src[idx:].rstrip()
            parts.append(split_defs[i])
            continue
        if i in spec["constants"]:
            parts.append(strip_imports(src))
            continue
        parts.append(src)

    if config_blocks:
        joined = "\n\n".join(config_blocks)
        parts.append(f"""
{BANNER}
# CONFIGURATION, THE DEFAULTS USED WHEN NOTHING IS PASSED IN
{BANNER}
#
# These mirror the notebook's configuration cell(s). They are module level so the module can be
# imported and driven from another script without editing it, while a plain run still behaves like
# the notebook. `dpm.config` overrides them from config/config.toml when that file exists, and the
# command line overrides both.

{joined}
""")

    footer = (FOOTER_DIR / f"{name}.py.txt").read_text(encoding="utf-8")
    # The footer may need the statements that were split out of a definition cell
    for idx, run in split_runs.items():
        footer = footer.replace(f"{{{{SPLIT_{idx}}}}}", textwrap.indent(run, "    "))
    parts.append(footer.rstrip())

    text = "\n\n".join(p.rstrip() for p in parts if p.strip()) + "\n"
    return re.sub(r"\n{4,}", "\n\n\n", text)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="compare against the committed modules instead of writing them")
    args = ap.parse_args(argv)

    failed = False
    for name, spec in SPECS.items():
        text = build_module(name, spec)
        target = OUT_DIR / f"{name}.py"
        if args.check:
            current = target.read_text(encoding="utf-8") if target.exists() else ""
            if current != text:
                failed = True
                print(f"DRIFT: {target.relative_to(ROOT)} differs from its notebook")
                diff = difflib.unified_diff(current.splitlines(), text.splitlines(),
                                            "committed", "regenerated", lineterm="", n=1)
                print("\n".join(list(diff)[:40]))
            else:
                print(f"ok: {target.relative_to(ROOT)} matches its notebook")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
            print(f"wrote {target.relative_to(ROOT)} ({len(text.splitlines())} lines)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
