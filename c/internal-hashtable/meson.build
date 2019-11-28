project('internal-hash', 'c')
cunit_sp = subproject('cunit')
cunit_dep = declare_dependency(link_with : cunit, include_directories : include)

incdir = include_directories('.')

executable('internal-hash', 'main.c','inthash.c',
  include_directories : incdir,
  dependencies : cunit_dep.get_variable('foobar_dep'))
