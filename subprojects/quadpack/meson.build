project('quadpack', 'fortran')

project_source_files = [
    'dqagi.f',
    'dqagie.f',
    'dqags.f',
    'dqagse.f',
    'dqelg.f',
    'dqk15i.f',
    'dqk21.f',
    'dqng.f',
    'dqpsrt.f',
]

project_target = static_library(
    meson.project_name(),
    project_source_files,
    dependencies: [dependency('openmp'), dependency('threads')]

)

project_dep = declare_dependency(link_with: project_target)
set_variable(meson.project_name() + '_dep', project_dep)
