#!/usr/bin/env python3
"""Generate pfac/consts.py from subprojects/faclib/consts.h.

Usage:
  make_consts.py           print the generated module to stdout
  make_consts.py --write   write the tracked source-tree fallback
  make_consts.py --check   exit non-zero if the tracked fallback is
                                    missing or out of sync
"""

import sys
from pathlib import Path

HEADER = "# Generated from consts.h (subprojects/faclib/consts.h) by make_consts.py -- do not edit.\n\n"


def parse_consts(consts_h):
    """Mirror of upstream setup.py parse_consts() parsing/write logic."""
    consts = list[tuple[str, str]]()
    with Path(consts_h).open("r") as f:
        for line in f:
            a = line.strip().split()
            if len(a) < 3 or a[0] != "#define" or a[1] == "_CONSTS_H_":
                continue
            name = a[1].removeprefix("_")
            value = a[2].strip("()")

            try:
                float(value)
            except ValueError:
                continue
            consts.append((name, value))
    return consts


def main(argv):
    write = "--write" in argv
    check = "--check" in argv

    consts_h = Path(__file__).resolve().parent / "subprojects" / "faclib" / "consts.h"
    fallback_path = Path(__file__).resolve().parent / "pfac" / "consts.py"

    content = (
        HEADER
        + "\n".join(f"{name} = {value}" for name, value in parse_consts(consts_h))
        + "\n"
    )

    if check:
        if not fallback_path.exists():
            raise SystemExit("Missing pfac/consts.py")
        if fallback_path.read_text() != content:
            raise SystemExit(
                "pfac/consts.py is out of sync with consts.h; "
                "regenerate it with: make_consts.py --write"
            )
    elif write:
        fallback_path.write_text(content)
    else:
        sys.stdout.write(content)


if __name__ == "__main__":
    main(sys.argv[1:])
