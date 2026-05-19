project('mpfun', 'fortran')

project_source_files = [
 'dxadd.f',
 'dxadj.f',
 'dxlegf.f',
 'dxpmu.f',
 'dxpmup.f',
 'dxpnrm.f',
 'dxpqnu.f',
 'dxpsi.f',
 'dxqmu.f',
 'dxqnu.f',
 'dxred.f',
 'dxset.f',
 'fdump.f',
 'i1mach.f',
 'j4save.f',
 'mpfun.f',
 'xercnt.f',
 'xerhlt.f',
 'xermsg.f',
 'xerprn.f',
 'xersve.f',
 'xgetua.f',
]

project_target = static_library(
    meson.project_name(),
    project_source_files,
    dependencies: [dependency('openmp'), dependency('threads')]
)

project_dep = declare_dependency(link_with: project_target)
set_variable(meson.project_name() + '_dep', project_dep)
