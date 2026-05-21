# Flexible Atomic Code

## __NOTE__ this is an experimental fork of FAC that uses meson instead of make in the hopes of improving the installation experience of pfac

The original unmodified code can be found [here](https://github.com/flexible-atomic-code/fac).

# Requirements
To install fac using this fork you need:
  - C compiler (gcc)
  - Fortran compiler (gfortran)
  - A unix like operating system (Linux or MacOS)
  - Python along with pip (usually preinstalled)

# Installation
I recommend creating a python virtual environment before proceding but it is not technically necessary.
Within that environment you can then simply write:

```pip install git+https://github.com/jajo-11/fac_meson```

That's it!

# Limitations
  - This has only been tested with gfortran, the original build system added some defines depending on the compiler, this forke does not which probably causes misbehavior in those cases.
  - OpenMp is always enabled
  - MPI is always disabled

# Reporting Issues
If you encounter build issues or crashes related to missing symbols create an issue on this github page first. And only if you have verified that it is unrelated to the modifications of this fork you should escalate to the upstream repository [here](https://github.com/flexible-atomic-code/fac).
