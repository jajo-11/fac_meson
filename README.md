# Flexible Atomic Code

> [!IMPORTANT]
> This is an __experimental__ fork of FAC that uses meson instead of make in the hopes of improving the installation experience of pfac

> [!Tip]
> The original unmodified code can be found [here](https://github.com/flexible-atomic-code/fac).

# Requirements
To install fac using this fork you need:
  - C compiler (gcc)
  - Fortran compiler (gfortran)
  - A unix like operating system (Linux, MacOS or [Windows*](#windows))
  - Python along with pip (usually preinstalled)

# Installation
I recommend creating a python virtual environment before proceding but it is not technically necessary.
Within that environment you can then simply write:

```bash
pip install git+https://github.com/jajo-11/fac_meson
```

That's it!

## Windows
On Windows the build requires a MinGW-w64 toolchain containing **both** `gcc`
and `gfortran` on the `PATH`.

An easy way to get these is [WinLibs](https://winlibs.com/). Just choose the download from the _Help! I don't know which download to choose!_ section and extract the zip and add the bin folder within to your `PATH`.

Then, with Python and pip installed:

```bash
pip install git+https://github.com/jajo-11/fac_meson
```

# Limitations
  - This has only been tested with gfortran, the original build system added some defines depending on the compiler, this forke does not which probably causes misbehavior in those cases.
  - OpenMp is always enabled
  - MPI is always disabled

# Reporting Issues
If you encounter build issues or crashes related to missing symbols create an issue on this github page first. And only if you have verified that it is unrelated to the modifications of this fork you should escalate to the upstream repository [here](https://github.com/flexible-atomic-code/fac).
