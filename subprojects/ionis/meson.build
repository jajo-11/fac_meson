project('ionis', 'fortran')

project_source_files = [
    'beli.f',
    'cfit.f',
    'colfit.f',
    'drfit.f',
    'intexp.f',
    'ionis.f',
    'ndrfit.f',
    'nrrfit.f',
    'phfit2.f',
    'recomb.f',
    'recomb_Fe.f',
    'rrfit.f',
]

project_target = static_library(
    meson.project_name(),
    project_source_files,
    dependencies: [dependency('openmp'), dependency('threads')]
)

project_dep = declare_dependency(link_with: project_target)
set_variable(meson.project_name() + '_dep', project_dep)
