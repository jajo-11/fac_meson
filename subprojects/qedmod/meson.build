project('qedmod', 'fortran')

project_source_files = [
    'atom_data.f',
    'dirac.f',
    'fse_dat.f',
    'genqed.f',
    'iniqed.f',
    'integr.f',
    'nucl.f',
    'pot_wav.f',
    'se_pot.f',
    'segrid.f',
    'uehling.f',
    'wk.f',
]

project_target = static_library(
    meson.project_name(),
    project_source_files,
    dependencies: [dependency('openmp'), dependency('threads')]

)

project_dep = declare_dependency(link_with: project_target)
set_variable(meson.project_name() + '_dep', project_dep)
