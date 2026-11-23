"""Run the FAC demo scripts and compare their output against reference data.

Usage examples::

    python check.py                    # run every fast demo, then check it
    python check.py -c                 # only compare existing output vs ref/
    python check.py -l                 # list demos, scripts and results
    python check.py structure NeL      # restrict to a couple of demos
    python check.py -R tests           # re-baseline demo/tests/ref
    python check.py -C                 # remove generated demo output
    python check.py -j8 --openmp       # parallel OpenMP run (no comparison)

Passing two file names keeps the historical single-file behaviour::

    python check.py ne.lev ref/ne.lev
"""

import argparse
import shutil
import subprocess
import sys
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

from pfac.rfac import *

DEMO_DIR = Path(__file__).resolve().parent


def _check_header(actual, expected):
    if "E0" in actual:
        if not np.allclose(actual["E0"], expected["E0"], rtol=0.01):
            raise ValueError(
                "header E0 mismatch: {} vs {}".format(actual["E0"], expected["E0"])
            )
    if "NBlocks" in actual:
        if actual["NBlocks"] != expected["NBlocks"]:
            raise ValueError(
                "header NBlocks mismatch: {} vs {}".format(
                    actual["NBlocks"], expected["NBlocks"]
                )
            )


def _check_block(actual_blocks, expected_blocks, atols={}, rtols={}):
    """Compare each values in two blocks.
    atol: mapping from key to corresponding maximum absolute errors.
    rtol: mapping from key to corresponding maximum relative errors.
    """

    def _raise(id, key, actual, expected):
        message = "Large difference is found in block {} key {}.".format(id, key)
        if isinstance(actual, np.ndarray):
            ind_a = np.unravel_index(np.argmax(np.abs(actual - expected)), actual.shape)
            ind_r = np.unravel_index(
                np.argmax(
                    0.5
                    * np.abs(actual - expected)
                    / (np.abs(actual) + np.abs(expected))
                ),
                actual.shape,
            )
            message += " The largest abs difference is in {}".format(ind_a)
            message += " with {} vs {} ".format(actual[ind_a], expected[ind_a])
            message += " The largest rel difference is in {}".format(ind_r)
            message += " with {} vs {} ".format(actual[ind_r], expected[ind_r])
        else:
            message += " {} vs {}".format(actual, expected)
        raise ValueError(message)

    if len(actual_blocks) != len(expected_blocks):
        raise ValueError(
            "number of blocks differs: {} vs {}".format(
                len(actual_blocks), len(expected_blocks)
            )
        )

    for i, (actual_bl, expected_bl) in enumerate(zip(actual_blocks, expected_blocks)):
        for key in actual_bl:
            if key not in expected_bl:
                raise ValueError(
                    "block {}: key {} is missing from the reference".format(i, key)
                )
            actual = actual_bl[key]
            expected = expected_bl[key]

            if isinstance(actual, np.ndarray):
                if actual.dtype.kind in "ifc":
                    if not np.allclose(
                        actual_bl[key],
                        expected_bl[key],
                        atol=atols.get(key, 1.0e-8),
                        rtol=rtols.get(key, 1.0e-5),
                    ):
                        _raise(i, key, actual, expected)
                else:  # string array
                    if not (actual == expected).all():
                        raise ValueError("found in inconsistency in {}".format(key))

            elif isinstance(actual, list):  # list of np.ndarray
                for ac, ex in zip(actual_bl[key], expected_bl[key]):
                    if not np.allclose(
                        ac, ex, atol=atols.get(key, 1.0e-8), rtol=rtols.get(key, 1.0e-5)
                    ):
                        _raise(i, key, actual, expected)

            elif isinstance(actual, float):
                if not np.allclose(
                    actual_bl[key],
                    expected_bl[key],
                    atol=atols.get(key, 1.0e-8),
                    rtol=rtols.get(key, 1.0e-5),
                ):
                    _raise(i, key, actual, expected)
            else:
                if not actual == expected:
                    raise ValueError(
                        "block {} key {} differs: {} vs {}".format(
                            i, key, actual, expected
                        )
                    )


def _sort_array(arrays, ref_arrays, *keys):
    """Sort arrays so that arrays[key] == ref_arrays[key]"""
    size = len(ref_arrays[keys[0]])

    new_indexes = np.zeros(size, dtype=int)
    for j in range(size):
        for i in range(size):
            if all(ref_arrays[k][i] == arrays[k][j] for k in keys):
                new_indexes[i] = j
                break

    new_arrays = OrderedDict()
    for k, v in arrays.items():
        if isinstance(v, np.ndarray) and len(v) == size:
            new_arrays[k] = v[new_indexes]
        elif isinstance(v, list) and len(v) == size:
            new_arrays[k] = []
            for ind in new_indexes:
                new_arrays[k].append(v[ind])
        else:
            new_arrays[k] = v

    return new_arrays


def check_en(actual_file, expected_file):
    actual_header, actual_blocks = read_lev(actual_file)
    expected_header, expected_blocks = read_lev(expected_file)

    _check_header(actual_header, expected_header)
    _check_block(
        actual_blocks, expected_blocks, atols={"ENERGY": 1.0e1}, rtols={"ENERGY": 0.01}
    )


def check_ai(actual_file, expected_file):
    actual_header, actual_blocks = read_ai(actual_file)
    expected_header, expected_blocks = read_ai(expected_file)

    # we need to sort arrays, because with openmp, the order may differ
    actual_blocks = [
        _sort_array(ac, ex, "bound_index", "free_index")
        for ac, ex in zip(actual_blocks, expected_blocks)
    ]

    _check_header(actual_header, expected_header)
    _check_block(
        actual_blocks,
        expected_blocks,
        atols={"rate": 1.0e1, "Delta E": 0.5},
        rtols={
            "rate": 0.05,
            "DC strength": 0.05,
            "AI rate": 0.05,
            "Delta E": 0.01,
            "EGRID": 1.0e-2,
        },
    )


def check_tr(actual_file, expected_file):
    actual_header, actual_blocks = read_tr(actual_file)
    expected_header, expected_blocks = read_tr(expected_file)

    # we need to sort arrays, because with openmp, the order may differ
    actual_blocks = [
        _sort_array(ac, ex, "lower_index", "upper_index")
        for ac, ex in zip(actual_blocks, expected_blocks)
    ]

    _check_header(actual_header, expected_header)
    _check_block(
        actual_blocks,
        expected_blocks,
        atols={"Delta E": 1.0e0, "gf": 1.0e-4, "rate": 1.0e4, "multipole": 1.0e-5},
        rtols={"Delta E": 0.01, "gf": 0.02, "rate": 0.05, "multipole": 0.05},
    )


def check_ce(actual_file, expected_file):
    actual_header, actual_blocks = read_ce(actual_file)
    expected_header, expected_blocks = read_ce(expected_file)

    # we need to sort arrays, because with openmp, the order may differ
    actual_blocks = [
        _sort_array(ac, ex, "lower_index", "upper_index")
        for ac, ex in zip(actual_blocks, expected_blocks)
    ]

    _check_header(actual_header, expected_header)
    _check_block(
        actual_blocks,
        expected_blocks,
        atols={
            "Delta E": 1.0e0,
            "bethe": 1.0e0,
            "born": 1.0,
            "collision strength": 0.001,
            "crosssection": 0.01,
            "TEGRID": 1.0,
            "EGRID": 1.0,
            "USR": 1.0,
            "TE0": 1.0,
            "ratio collision strength": 0.1,
        },
        rtols={
            "Delta E": 0.01,
            "bethe": 0.05,
            "born": 0.05,
            "collision strength": 0.05,
            "crosssection": 0.1,
            "TEGRID": 0.01,
            "EGRID": 0.01,
            "USR": 0.01,
            "TE0": 0.01,
            "ratio collision strenth": 0.05,
        },
    )


def check_ci(actual_file, expected_file):
    actual_header, actual_blocks = read_ci(actual_file)
    expected_header, expected_blocks = read_ci(expected_file)

    # we need to sort arrays, because with openmp, the order may differ
    actual_blocks = [
        _sort_array(ac, ex, "bound_index", "free_index")
        for ac, ex in zip(actual_blocks, expected_blocks)
    ]

    _check_header(actual_header, expected_header)
    _check_block(
        actual_blocks,
        expected_blocks,
        atols={
            "Delta E": 1.0e0,
            "bethe": 1.0e0,
            "born": 1.0,
            "collision strength": 0.001,
            "crosssection": 0.01,
            "TEGRID": 1.0,
            "EGRID": 1.0,
            "USR": 1.0,
            "TE0": 1.0,
        },
        rtols={
            "Delta E": 0.01,
            "bethe": 0.01,
            "born": 0.01,
            "collision strength": 0.02,
            "crosssection": 0.1,
            "TEGRID": 0.01,
            "EGRID": 0.01,
            "USR": 0.01,
            "TE0": 0.01,
            "parameters": 0.01,
        },
    )


def check_rr(actual_file, expected_file):
    actual_header, actual_blocks = read_rr(actual_file)
    expected_header, expected_blocks = read_rr(expected_file)

    # we need to sort arrays, because with openmp, the order may differ
    actual_blocks = [
        _sort_array(ac, ex, "bound_index", "free_index")
        for ac, ex in zip(actual_blocks, expected_blocks)
    ]

    _check_header(actual_header, expected_header)
    _check_block(
        actual_blocks,
        expected_blocks,
        atols={
            "Delta E": 1.0e0,
            "bethe": 1.0e0,
            "born": 1.0,
            "TEGRID": 1.0,
            "EGRID": 1.0,
            "USR": 1.0,
            "TE0": 1.0,
        },
        rtols={
            "Delta E": 0.01,
            "bethe": 0.01,
            "born": 0.01,
            "RR crosssection": 0.01,
            "PI crosssection": 0.01,
            "TEGRID": 0.01,
            "EGRID": 0.01,
            "USR": 0.01,
            "TE0": 0.01,
            "parameters": 0.01,
            "gf": 0.01,
        },
    )


def check_sp(actual_file, expected_file):
    actual_header, actual_blocks = read_sp(actual_file)
    expected_header, expected_blocks = read_sp(expected_file)

    _check_header(actual_header, expected_header)
    _check_block(
        actual_blocks,
        expected_blocks,
        atols={
            "Delta E": 1.0e0,
            "abs. energy": 1.0e0,
            "emissivity": 1.0e-10,
            "population": 1.0e-30,
        },
        rtols={
            "Delta E": 0.01,
            "abs. energy": 0.01,
            "emissivity": 0.05,
            "population": 0.05,
        },
    )


def check_rt(actual_file, expected_file):
    actual_header, actual_blocks = read_rt(actual_file)
    expected_header, expected_blocks = read_rt(expected_file)

    _check_header(actual_header, expected_header)
    _check_block(actual_blocks, expected_blocks)


def check_ham(actual_file, expected_file):
    actual_header, actual_blocks = read_ham(actual_file)
    expected_header, expected_blocks = read_ham(expected_file)

    _check_header(actual_header, expected_header)
    _check_block(
        actual_blocks, expected_blocks, atols={"value": 1e-5}, rtols={"value": 1e-3}
    )


def check(actual_file, expected_file):
    if actual_file[-3:] in [".en", "lev"]:
        check_en(actual_file, expected_file)

    elif actual_file[-3:] == ".ai":
        check_ai(actual_file, expected_file)

    elif actual_file[-3:] == ".tr":
        check_tr(actual_file, expected_file)

    elif actual_file[-3:] in [".ce", "ceM"]:
        check_ce(actual_file, expected_file)

    elif actual_file[-3:] == ".ci":
        check_ci(actual_file, expected_file)

    elif actual_file[-3:] == ".rr":
        check_rr(actual_file, expected_file)

    elif actual_file[-3:] == ".sp":
        check_sp(actual_file, expected_file)

    elif actual_file[-3:] == ".rt":
        check_rt(actual_file, expected_file)

    elif actual_file[-4:] == ".ham":
        check_ham(actual_file, expected_file)

    else:
        raise TypeError("Unknown file extension: {}".format(actual_file))


# ---------------------------------------------------------------------------
# demo registry
#
#   scripts  : the example scripts to run, in order, with cwd = the demo dir
#   results  : files compared against ref/, and re-baselined by --update-ref
#   outputs   : everything generated, removed by --clean
#   slow      : only run when the demo is named explicitly or --all is given
#   unchecked : generated files that have no checker (documented, not compared)
# ---------------------------------------------------------------------------

DEMOS = OrderedDict(
    [
        (
            "structure",
            dict(
                scripts=["fe17_structure.py"],
                results=["ne.lev", "ne.tr"],
                outputs=["ne.pot", "ne.lev.b", "ne.lev", "ne.tr.b", "ne.tr"],
                openmp=True,
            ),
        ),
        (
            "excitation",
            dict(
                scripts=["fe17_excitation.py", "fe17_excitationM.py"],
                results=["ne.lev", "ne.ce", "ne.ceM"],
                outputs=[
                    "ne.lev.b",
                    "ne.lev",
                    "ne.ce.b",
                    "ne.ce",
                    "ne.ceM.b",
                    "ne.ceM",
                ],
                openmp=True,
            ),
        ),
        (
            "pirr",
            dict(
                scripts=["fe24_pirr.py"],
                results=["li.lev", "li.rr"],
                outputs=["li.lev.b", "li.lev", "li.rr.b", "li.rr"],
            ),
        ),
        (
            "aidr",
            dict(
                scripts=["se_ai.py"],
                results=["se.lev", "se.ai"],
                outputs=["se.lev.b", "se.lev", "se.ai.b", "se.ai"],
            ),
        ),
        (
            "ionization",
            dict(
                scripts=["fe17_ionization.py"],
                results=["ne_f.lev", "ne.ci"],
                outputs=["ne_f.lev.b", "ne_f.lev", "ne.ci.b", "ne.ci"],
                openmp=True,
            ),
        ),
        (
            "polariz",
            dict(
                scripts=["data.py", "pol.py"],
                results=["ta.en", "ta.tr", "ta.ce"],
                outputs=[
                    "ta.en",
                    "ta.tr",
                    "ta.ce",
                    "tb.en",
                    "tb.tr",
                    "tb.ce",
                    "pol.txt",
                    "pop.txt",
                ],
                unchecked=["pol.txt", "pop.txt"],
            ),
        ),
        (
            "NeL",
            dict(
                scripts=["ne.py", "spec.py"],
                results=[
                    "Ne03a.en",
                    "Ne03a.tr",
                    "Ne03a.ce",
                    "Ne03a.rt",
                    "Ne03a.sp",
                    "Ne03b.ham",
                ],
                outputs=["Ne03a.r0", "Ne03a.r1", "Ne03a.r3"]
                + ["Ne03a.%s" % e for e in ("en", "tr", "ce", "rt", "sp")]
                + ["Ne03b.%s" % e for e in ("en", "tr", "ce", "rt", "sp", "ham")],
                openmp=True,
            ),
        ),
        (
            "tests",
            dict(
                scripts=["simple_crm.py", "diag_hamiltonian.py", "maxwell_rate.py"],
                results=["diagh_O_a.en", "O.sp"],
                outputs=[
                    "diagh_O.en",
                    "diagh_O_a.en",
                    "O.b.sp",
                    "O.sp",
                    "Nea.en",
                    "Neb.en",
                    "Neb.tr",
                    "Neb.ce",
                    "Neb.cer",
                    "Neb.ci",
                    "Neb.cir",
                    "Neb.ham",
                ],
                globs=["O_crm"],
                openmp=True,
            ),
        ),
        (
            "FeL",
            dict(
                scripts=["fe.py", "spec.py"],
                results=[],
                outputs=[],
                globs=["data", "Fe08", "Fe09", "Fe10"],
                slow=True,
            ),
        ),
        (
            "rmatrix",
            dict(
                scripts=["rmx.py", "cs.py"],
                results=[],
                outputs=[],
                globs=["rmx.b*", "rmx.d*", "r1.d*"],
                slow=True,
            ),
        ),
    ]
)


def default_demos():
    """All demos that have reference data, i.e. the ones we can regress."""
    return [n for n, d in DEMOS.items() if d.get("results") and not d.get("slow")]


def demo_dir(name):
    return DEMO_DIR / name


def run_demo(name, openmp=False, verbose=False):
    """Run a demo's scripts in order; raise RuntimeError on the first failure."""
    info = DEMOS[name]
    cwd = demo_dir(name)
    for script in info["scripts"]:
        cmd = [sys.executable, script]
        # only some scripts understand the optional 'openmp' argument
        if openmp and info.get("openmp"):
            cmd.append("openmp")
        if verbose:
            print("  $ %s" % " ".join(cmd), flush=True)
        proc = subprocess.run(cmd, cwd=str(cwd))
        if proc.returncode != 0:
            raise RuntimeError(
                "%s/%s exited with status %d" % (name, script, proc.returncode)
            )


def check_demo(name, verbose=False):
    """Compare a demo's results against ref/; return a list of problems."""
    info = DEMOS[name]
    cwd = demo_dir(name)
    problems = []
    for result in info["results"]:
        actual = cwd / result
        expected = cwd / "ref" / result
        if verbose:
            print("  %s vs ref/%s" % (result, result), flush=True)
        if not actual.exists():
            problems.append("%s: missing (run the demo first)" % actual.name)
            continue
        if not expected.exists():
            problems.append("ref/%s: missing reference file" % result)
            continue
        try:
            check(str(actual), str(expected))
        except Exception as e:
            problems.append("%s: %s" % (result, e))
    return problems


def update_ref(name, verbose=False):
    """Copy a demo's current results into ref/, creating it if needed."""
    info = DEMOS[name]
    if not info["results"]:
        return
    refdir = demo_dir(name) / "ref"
    refdir.mkdir(exist_ok=True)
    for result in info["results"]:
        src = demo_dir(name) / result
        if not src.exists():
            raise RuntimeError("%s: cannot re-baseline, file was not produced" % result)
        if verbose:
            print("  %s -> ref/%s" % (result, result), flush=True)
        shutil.copyfile(src, refdir / result)


def clean_demo(name, verbose=False):
    """Remove generated output so the next run starts from scratch."""
    info = DEMOS[name]
    cwd = demo_dir(name)
    paths = [cwd / o for o in info.get("outputs", [])]
    for pattern in info.get("globs", []):
        paths.extend(cwd.glob(pattern))
    for path in paths:
        if path.is_dir():
            if verbose:
                print("  rm -r %s" % path, flush=True)
            shutil.rmtree(path)
        elif path.exists():
            if verbose:
                print("  rm %s" % path, flush=True)
            path.unlink()


def list_demos():
    print("%-12s %-8s %s" % ("demo", "refs", "scripts"))
    for name, info in DEMOS.items():
        missing = [s for s in info["scripts"] if not (demo_dir(name) / s).exists()]
        note = ""
        if not info["results"]:
            note = "  (no reference data)"
        elif info.get("slow"):
            note = "  (slow, opt in by name)"
        if missing:
            note += "  MISSING: " + " ".join(missing)
        print(
            "%-12s %-8s %s%s"
            % (name, len(info["results"]), " ".join(info["scripts"]), note)
        )
        if info.get("unchecked"):
            print(
                "%-12s %-8s produced but not compared: %s"
                % ("", "", " ".join(info["unchecked"]))
            )


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check.py",
        description="Run the FAC demos and compare their output with ref/.",
        epilog="Two file arguments keep the old behaviour: check.py FILE REF.",
    )
    parser.add_argument(
        "names",
        nargs="*",
        metavar="DEMO",
        help="demos to act on (default: %s)" % " ".join(default_demos()),
    )
    parser.add_argument("-l", "--list", action="store_true", help="list demos")
    parser.add_argument("-r", "--run", action="store_true", help="run the demo scripts")
    parser.add_argument(
        "-c", "--check", action="store_true", help="compare results with ref/"
    )
    parser.add_argument(
        "-C", "--clean", action="store_true", help="remove generated output"
    )
    parser.add_argument(
        "-R",
        "--update-ref",
        action="store_true",
        help="re-baseline ref/ from a fresh run (implies --run)",
    )
    parser.add_argument(
        "-k",
        "--keep-going",
        action="store_true",
        help="continue after a failing demo instead of stopping",
    )
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        default=1,
        metavar="N",
        help="run up to N demos at once (default: 1)",
    )
    parser.add_argument(
        "--openmp",
        action="store_true",
        help="run the scripts that support it with OpenMP (implies --run)",
    )
    parser.add_argument(
        "--all",
        dest="all_demos",
        action="store_true",
        help="include slow demos and demos without reference data",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    # historical single-file mode: check.py FILE REF
    if len(args.names) == 2 and all(Path(n).is_file() for n in args.names):
        print(args.names[0])
        check(args.names[0], args.names[1])
        return 0

    if args.list:
        list_demos()
        return 0

    # work out what to do; no action flags means run + check, except for
    # --openmp where the serial ref/ data cannot be compared against
    if not (args.run or args.check or args.clean or args.update_ref):
        args.run = True
        if args.openmp:
            print(
                "note: --openmp only runs the demos; ref/ holds serial output, so "
                "pass -c explicitly if you want to compare anyway",
                file=sys.stderr,
            )
        else:
            args.check = True
    if args.update_ref:
        args.run, args.check = True, False

    if args.names:
        unknown = [n for n in args.names if n not in DEMOS]
        if unknown:
            parser.error("unknown demo(s): %s" % ", ".join(unknown))
        names = list(args.names)
    elif args.all_demos:
        names = list(DEMOS)
    else:
        names = default_demos()

    if args.jobs < 1:
        parser.error("--jobs must be a positive integer")
    if args.jobs > 1 and not args.keep_going:
        print(
            "note: --jobs implies --keep-going (each demo runs independently)",
            file=sys.stderr,
        )
        args.keep_going = True

    def process(name):
        """clean/run/re-baseline/check one demo; returns a list of problems."""
        print("==> %s" % name, flush=True)
        problems = []
        if args.clean:
            try:
                clean_demo(name, args.verbose)
            except Exception as e:
                problems.append("clean: %s" % e)
        # a demo with no reference data cannot be re-baselined, so -R must not
        # silently turn into a plain (possibly very slow) run
        should_run = args.run and (not args.update_ref or DEMOS[name]["results"])
        if should_run and not problems:
            try:
                run_demo(name, args.openmp, args.verbose)
            except Exception as e:
                problems.append(str(e))
        if args.update_ref and not problems:
            try:
                update_ref(name, args.verbose)
            except Exception as e:
                problems.append("update-ref: %s" % e)
        if args.check and not problems:
            problems.extend(check_demo(name, args.verbose))
        return name, problems

    results = {}
    if args.jobs > 1 and len(names) > 1:
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            for name, problems in pool.map(process, names):
                results[name] = problems
    else:
        for name in names:
            _, problems = process(name)
            results[name] = problems
            if problems and not args.keep_going:
                break

    failed = [n for n in names if results.get(n)]
    ran = [n for n in names if n in results]

    if len(names) > 1 or failed:
        print()
        for name in names:
            if name not in results:
                print("%-12s skipped (stopped after an earlier failure)" % name)
            elif results[name]:
                print("%-12s FAILED" % name)
            else:
                print("%-12s ok" % name)
        print()

    if failed:
        for name in failed:
            for problem in results[name]:
                print("FAILED %s: %s" % (name, problem), file=sys.stderr)
        return 1

    if args.check:
        if any(DEMOS[n]["results"] for n in names):
            print("All demos match their reference data.")
        else:
            print("No demo in this selection has reference data to compare.")
    elif args.update_ref:
        rebaselined = [n for n in ran if DEMOS[n]["results"]]
        if rebaselined:
            print("Re-baselined ref/ for: %s" % " ".join(rebaselined))
        else:
            print("Nothing to re-baseline, this selection has no reference data.")
    elif args.clean:
        print("Removed generated demo output.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
