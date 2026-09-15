#!/usr/bin/env python3
"""Command line entry point for all three pipelines.

One CLI rather than three, so there is a single place to learn and a single place where paths are
resolved. Each subcommand maps to one pipeline module:

    dpm relapse        --workflow both     relapse calculation, then population extrapolation
    dpm tipping-point                      the four 1D tipping point figures and the PDF report
    dpm dual-use                           rebuild the Difference tab as Difference_calc
    dpm self-test                          run every pipeline on synthetic data

Path resolution is deliberately layered: module defaults, then ``config/config.toml``, then
``DPM_*`` environment variables, then whatever is passed here. A value given on the command line
always wins, which is what makes the same checkout usable by two analysts with different folders.

Run ``dpm <command> --help`` for the options of one command.
"""
from __future__ import annotations

import argparse
import sys

from pathlib import Path

from dpm import __version__, config


def _resolve(cli_value, section: str, key: str, cfg: dict):
    """Command line first, then the config file, then None so the module default applies."""
    return cli_value if cli_value is not None else config.get(section, key, None, cfg)


def _dir(cli_value, section: str, key: str, cfg: dict):
    """Resolve a folder, with different bases depending on where the value came from.

    A path typed on the command line is relative to the current working directory, because that is
    what every other command line tool does and ``--dir .`` has to mean "here". A path in
    ``config/config.toml`` is relative to the repository root, because the config file lives there
    and refers to folders like ``data/raw`` that belong to the checkout, not to wherever the user
    happens to be standing.
    """
    if cli_value is not None:
        return str(Path(cli_value).expanduser().resolve())
    resolved = config.resolve_dir(config.get(section, key, None, cfg))
    return str(resolved) if resolved else None


# --------------------------------------------------------------------------- commands
def cmd_relapse(args, cfg) -> int:
    from dpm import relapse_popextrapolation as rp

    data_dir = _dir(args.dir, "paths", "data_dir", cfg)
    out_dir = _dir(args.out_dir, "paths", "out_dir", cfg)
    results_file = _resolve(args.relapse_output, "relapse", "output_file", cfg)

    if args.workflow in ("1", "both"):
        print("=" * 70, "\nWORKFLOW 1, relapse calculation\n", "=" * 70, sep="")
        rp.run_workflow1(working_dir=data_dir,
                         infile=_resolve(args.relapse_input, "relapse", "input_file", cfg),
                         outfile=results_file, out_dir=out_dir)

    if args.workflow in ("2", "both"):
        print("\n" + "=" * 70, "\nWORKFLOW 2, population extrapolation\n", "=" * 70, sep="")
        # Workflow 2 reads the workbook Workflow 1 wrote, so when both run in one command the
        # output folder of the first is the input folder of the second.
        rp.run_workflow2(working_dir=out_dir or data_dir,
                         rfile=results_file,
                         ifile=_resolve(args.params_input, "relapse", "params_file", cfg),
                         product_name=_resolve(args.product, "run", "product", cfg),
                         author_name=_resolve(args.author, "run", "author", cfg),
                         out_dir=out_dir)
    return 0


def cmd_tipping_point(args, cfg) -> int:
    from dpm import tipping_point_plotting as tp

    tp.run_analysis(data_dir=_dir(args.dir, "paths", "data_dir", cfg),
                    out_dir=_dir(args.out_dir, "paths", "out_dir", cfg),
                    author=_resolve(args.author, "run", "author", cfg),
                    export=not args.no_export,
                    validate=not args.no_validate)
    return 0


def cmd_dual_use(args, cfg) -> int:
    from dpm import dual_use_optimizer as du

    du.run_optimizer(data_dir=_dir(args.dir, "paths", "data_dir", cfg),
                     out_dir=_dir(args.out_dir, "paths", "out_dir", cfg),
                     filename=_resolve(args.input_file, "dual_use", "input_file", cfg),
                     validate=not args.no_validate)
    return 0


def cmd_self_test(args, cfg) -> int:
    """Every pipeline on synthetic data. No real export needed, so this is the smoke test."""
    from dpm import dual_use_optimizer as du
    from dpm import relapse_popextrapolation as rp
    from dpm import tipping_point_plotting as tp

    targets = {"relapse": rp.self_test, "tipping-point": tp.self_test, "dual-use": du.self_test}
    chosen = targets if args.pipeline == "all" else {args.pipeline: targets[args.pipeline]}

    for name, fn in chosen.items():
        print("\n" + "#" * 70, f"\n# SELF TEST: {name}\n", "#" * 70, sep="")
        fn()
    print("\nAll requested self tests passed.")
    return 0


# --------------------------------------------------------------------------- parser
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dpm",
        description="Dynamic Population Model analysis pipelines.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--version", action="version", version=f"dpm {__version__}")
    parser.add_argument("--config", default=None,
                        help="path to a TOML config file (default: config/config.toml)")
    subs = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--dir", default=None, help="folder holding the input workbooks")
    common.add_argument("--out-dir", default=None, help="write outputs somewhere else")
    common.add_argument("--author", default=None, help="name recorded on the outputs")

    p = subs.add_parser("relapse", parents=[common],
                        help="relapse calculation and population extrapolation",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--workflow", choices=["1", "2", "both"], default="both")
    p.add_argument("--relapse-input", default=None, help="Workflow 1 input, the DPM export")
    p.add_argument("--relapse-output", default=None,
                   help="Workflow 1 output, which is input 2 of Workflow 2")
    p.add_argument("--params-input", default=None,
                   help="Workflow 2 input 1, the parameters and births workbook")
    p.add_argument("--product", default=None,
                   help="override the product; by default it is read from Model Group")
    p.set_defaults(func=cmd_relapse)

    p = subs.add_parser("tipping-point", parents=[common],
                        help="1D tipping point figures, QC table and PDF report",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--no-export", action="store_true", help="skip the dated export bundle")
    p.add_argument("--no-validate", action="store_true", help="skip the post run checks")
    p.set_defaults(func=cmd_tipping_point)

    p = subs.add_parser("dual-use", parents=[common],
                        help="rebuild the Difference tab as Difference_calc",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--input-file", default=None,
                   help="name the workbook explicitly if the folder holds several")
    p.add_argument("--no-validate", action="store_true", help="skip the post run checks")
    p.set_defaults(func=cmd_dual_use)

    p = subs.add_parser("self-test", help="run the pipelines on synthetic data")
    p.add_argument("--pipeline", choices=["all", "relapse", "tipping-point", "dual-use"],
                   default="all")
    p.set_defaults(func=cmd_self_test)

    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    cfg = config.load(args.config)
    try:
        return args.func(args, cfg)
    except FileNotFoundError as exc:
        # An input that is not there is the most common failure and does not warrant a traceback
        print(f"\nInput not found: {exc}", file=sys.stderr)
        print("Check --dir, or config/config.toml, or run 'dpm self-test' to verify the install.",
              file=sys.stderr)
        return 2
    except (ValueError, KeyError, AssertionError) as exc:
        print(f"\n{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
