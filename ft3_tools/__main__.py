"""Build or check the public FT3 V1 generated catalog files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .catalog import CatalogError, load_catalog
from .export import render_catalog, stale_outputs, write_outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m ft3_tools")
    parser.add_argument("action", choices=("check", "build"))
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    args = parser.parse_args(argv)
    try:
        catalog = load_catalog(args.root)
        rendered = render_catalog(catalog)
        if args.action == "check":
            stale = stale_outputs(args.root, rendered)
            if stale:
                print("stale generated files: " + ", ".join(stale), file=sys.stderr)
                return 1
            print("generated catalog files are current")
            return 0
        write_outputs(args.root, rendered)
    except (CatalogError, OSError) as exc:
        print(f"FT3 catalog error: {exc}", file=sys.stderr)
        return 1
    print("generated four FT3 V1 catalog files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
