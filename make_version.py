from pathlib import Path

if __name__ == "__main__":
    consts_h = Path(__file__).parent.joinpath("subprojects/faclib/consts.h")
    version = 0
    subversion = 0
    subsubversion = 0
    with open(consts_h, "r") as f:
        for line in f:
            if line.startswith("#define VERSION"):
                version = int(line.split()[2].strip())
            if line.startswith("#define SUBVERSION"):
                subversion = int(line.split()[2].strip())
            if line.startswith("#define SUBSUBVERSION"):
                subsubversion = int(line.split()[2].strip())

    version_py = Path(__file__).parent.joinpath("pfac/version.py")
    with open(version_py, "w") as f:
        f.write(f'version = "{version}.{subversion}.{subsubversion}"')

    print(f"{version}.{subversion}.{subsubversion}")
