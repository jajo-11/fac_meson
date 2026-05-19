project('toms', 'fortran')

project_source_files = [
    'calcc.f',
    'dist.f',
    'evalf.f',
    'fdi.f',
    'fm1m.f',
    'fm1mi.f',
    'fm1p.f',
    'fm1pi.f',
    'fm3p.f',
    'fm3pi.f',
    'fm5p.f',
    'fm5pi.f',
    'fstats.f',
    'newpt.f',
    'order.f',
    'partx.f',
    'rgbi3p.f',
    'sdbi3p.f',
    'setstp.f',
    'simplx.f',
    'sortd.f',
    'start.f',
    'subopt.f',
    'subplx.f',
    'tn.f',
    'tripack.f',
    'uvip3c.f',
    'uvip3i.f',
    'uvip3p.f',
]

project_target = static_library(
    meson.project_name(),
    project_source_files,
    dependencies: [dependency('openmp'), dependency('threads')]

)

project_dep = declare_dependency(link_with: project_target)
set_variable(meson.project_name() + '_dep', project_dep)
