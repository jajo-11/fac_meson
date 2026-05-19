project('mblas', 'fortran')

project_source_files = [
    'dasum.f',
    'daxpy.f',
    'dcopy.f',
    'ddot.f',
    'dgemm.f',
    'dgemv.f',
    'dger.f',
    'dnrm2.f',
    'drot.f',
    'dscal.f',
    'dspmv.f',
    'dspr2.f',
    'dswap.f',
    'dtbsv.f',
    'dtrmm.f',
    'dtrmv.f',
    'dtrsm.f',
    'idamax.f',
    'lsame.f',
    'xerbla.f',
]

project_target = static_library(
    meson.project_name(),
    project_source_files,
    dependencies: [dependency('openmp'), dependency('threads')]

)

project_dep = declare_dependency(link_with: project_target)
set_variable(meson.project_name() + '_dep', project_dep)
