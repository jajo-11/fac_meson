project('faclib', ['c', 'fortran'])

project_source_files = [
    'angular.c',
    'array.c',
    'cfp.c',
    'config.c',
    'coulomb.c',
    'crm.c',
    'dbase.c',
    'excitation.c',
    'fftsg.c',
    'grid.c',
    'init.c',
    'interpolation.c',
    'ionization.c',
    'mbpt.c',
    'mmalloc.c',
    'mpiutil.c',
    'nucleus.c',
    'omalloc.c',
    'orbital.c',
    'parser.c',
    'pmalloc.c',
    'polarization.c',
    'radial.c',
    'rates.c',
    'rcfp.c',
    'recombination.c',
    'recouple.c',
    'rmatrix.c',
    'structure.c',
    'transition.c',
    'f2c.f90',
]

project_target = static_library(
    meson.project_name(),
    project_source_files,
    dependencies: [dependency('openmp'), dependency('threads')],
)

project_dep = declare_dependency(link_with: project_target, include_directories: include_directories('.'))
set_variable(meson.project_name() + '_dep', project_dep)
