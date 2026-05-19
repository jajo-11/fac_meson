project('minpack', 'fortran')

project_source_files = [
    'chkder.f',
    'dpmpar.f',
    'enorm.f',
    'lmder.f',
    'lmder1.f',
    'lmpar.f',
    'qrfac.f',
    'qrsolv.f',
]

project_target = static_library(
    meson.project_name(),
    project_source_files,
    dependencies: [dependency('openmp'), dependency('threads')]
)

project_dep = declare_dependency(link_with: project_target)
set_variable(meson.project_name() + '_dep', project_dep)
