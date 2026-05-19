project(
    'fac',
    'c',
    'fortran',
    version: run_command('python3', 'make_version.py', check: true).stdout().strip(),
)

blas_dep = subproject('mblas').get_variable('mblas_dep')
coul_dep = subproject('coul').get_variable('coul_dep')
ionis_dep = subproject('ionis').get_variable('ionis_dep')
lapack_dep = subproject('lapack').get_variable('lapack_dep')
minpack_dep = subproject('minpack').get_variable('minpack_dep')
qedmod_dep = subproject('qedmod').get_variable('qedmod_dep')
mpfun_dep = subproject('mpfun').get_variable('mpfun_dep')
ode_dep = subproject('ode').get_variable('ode_dep')
quadpack_dep = subproject('quadpack').get_variable('quadpack_dep')
toms_dep = subproject('toms').get_variable('toms_dep')
faclib_dep = subproject('faclib').get_variable('faclib_dep')

project_source_files = [
    'sfac/sfac.c',
    'sfac/stoken.c',
]

cc = meson.get_compiler('c')
m_dep = cc.find_library('m', required: false)

project_dependencies = [
    blas_dep,
    coul_dep,
    faclib_dep,
    ionis_dep,
    lapack_dep,
    minpack_dep,
    qedmod_dep,
    mpfun_dep,
    ode_dep,
    quadpack_dep,
    toms_dep,
    m_dep,
    dependency('openmp'),
    dependency('threads'),
]

executable(
    'sfac',
    [
        'sfac/sfac.c',
        'sfac/stoken.c',
    ],
    dependencies: project_dependencies,
    install: true,
)

executable(
    'scrm',
    [
        'sfac/scrm.c',
        'sfac/stoken.c',
    ],
    dependencies: project_dependencies,
    install: true,
)

executable(
    'spol',
    [
        'sfac/spol.c',
        'sfac/stoken.c',
    ],
    dependencies: project_dependencies,
    install: true,
)

py = import('python').find_installation(pure: false)

py.install_sources(
    [
        'pfac/__init__.py',
        'pfac/aa.py',
        'pfac/atom.py',
        'pfac/config.py',
        'pfac/const.py',
        'pfac/version.py',
        'pfac/rfac.py',
        'pfac/spm.py',
        'pfac/table.py',
    ],
    subdir: 'pfac',
)

py.extension_module('pfac', 'pfac/mpy.c', install: true, dependencies: project_dependencies)
py.extension_module(
    'fac',
    'pfac/fac.c',
    install: true,
    dependencies: project_dependencies,
    install_dir: py.get_install_dir() / 'pfac',
)
py.extension_module(
    'pcrm',
    'pfac/pcrm.c',
    install: true,
    dependencies: project_dependencies,
    install_dir: py.get_install_dir() / 'pfac',
)
py.extension_module(
    'ppol',
    'pfac/ppol.c',
    install: true,
    dependencies: project_dependencies,
    install_dir: py.get_install_dir() / 'pfac',
)
py.extension_module(
    'util',
    'pfac/util.c',
    install: true,
    dependencies: project_dependencies,
    install_dir: py.get_install_dir() / 'pfac',
)
