"""PEP 517 build backend wrapping meson-python.

Builds wheels via meson-python and, on Windows, repairs them with delvewheel
so the compiler runtime DLLs (libgcc, libgfortran, libgomp, libwinpthread,
libquadmath, ...) are vendored into the wheel. This makes every wheel built
from this tree self-contained, independent of the build machine's PATH.
"""

import os
import shutil
import subprocess
import sys
import tempfile

from mesonpy import (
    build_editable,
    build_sdist,
    get_requires_for_build_sdist,
    get_requires_for_build_wheel,
)
from mesonpy import build_wheel as _build_wheel


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    wheel_name = _build_wheel(wheel_directory, config_settings, metadata_directory)

    if sys.platform == "win32":
        wheel_path = os.path.join(wheel_directory, wheel_name)
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.check_call(
                [sys.executable, "-m", "delvewheel", "repair", "-w", tmp, wheel_path]
            )
            repaired = os.listdir(tmp)
            if repaired:
                shutil.move(os.path.join(tmp, repaired[0]), wheel_path)

    return wheel_name
