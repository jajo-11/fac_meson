project('ode', 'fortran')

project_source_files = [
    'cfode.f',
    'dgbfa.f',
    'dgbsl.f',
    'dgefa.f',
    'dgesl.f',
    'ewset.f',
    'intdy.f',
    'lsode.f',
    'prepj.f',
    'solsy.f',
    'stode.f',
    'vnorm.f',
    'xerrwv.f',
]

project_target = static_library(
    meson.project_name(),
    project_source_files,
    dependencies: [dependency('openmp'), dependency('threads')]

)

project_dep = declare_dependency(link_with: project_target)
set_variable(meson.project_name() + '_dep', project_dep)
