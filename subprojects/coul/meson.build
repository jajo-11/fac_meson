project('coul', 'fortran')

project_source_files = [
    'argam.f',
    'cmultip.f',
    'd1mach.f',
    'expint.f',
    'mohrfin.f',
    'beslik.f',
    'coulcc.f',
    'dcoul.f',
    'f11.f',
    'njintr.f',
    'besljn.f',
    'coulrad.f',
    'dlogam.f',
    'njsym.f',
    'clogam.f',
    'cphamp.f',
    'eione.f',
    'y5n.f',
]

project_target = static_library(
    meson.project_name(),
    project_source_files,
    dependencies: [dependency('openmp'), dependency('threads')]
)

project_dep = declare_dependency(link_with: project_target)
set_variable(meson.project_name() + '_dep', project_dep)
