#!/usr/bin/env python3
"""Print the FAC version parsed from subprojects/faclib/consts.h.

With --check, exit non-zero if the tracked source-tree fallback
pfac/version.py is missing or out of sync (used by .githooks/pre-commit).
"""
import re
import sys
from pathlib import Path


def fac_version():
    consts_h = Path(__file__).resolve().parent / "subprojects" / "faclib" / "consts.h"
    parts = {
        "VERSION": 0,
        "SUBVERSION": 0,
        "SUBSUBVERSION": 0,
    }
    with consts_h.open("r") as f:
        for line in f:
            for key in parts:
                if line.startswith(f"#define {key}"):
                    parts[key] = int(line.split()[2].strip())
    return "{VERSION}.{SUBVERSION}.{SUBSUBVERSION}".format(**parts)


def check_fallback(version):
    """Check the tracked source-tree pfac/version.py fallback."""
    version_py = Path(__file__).resolve().parent / "pfac" / "version.py"
    if not version_py.exists():
        raise SystemExit("Missing pfac/version.py")
    declared = None
    for line in version_py.read_text().splitlines():
        match = re.match(r"^version\s*=\s*['\"]([^'\"]+)['\"]", line.strip())
        if match:
            declared = match.group(1)
    if declared != version:
        raise SystemExit(f"Version mismatch between consts.h and version.py; ({declared!r} != {version!r})")


if __name__ == "__main__":
    strict = "--check" in sys.argv[1:]
    fac_version_ = fac_version()
    if strict:
        check_fallback(fac_version_)
    print(fac_version_)
