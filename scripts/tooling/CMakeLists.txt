project(TOOLING)
cmake_minimum_required(VERSION 2.8)
cmake_host_system_information(RESULT NUMCPU QUERY NUMBER_OF_LOGICAL_CORES)

include(ExternalProject)

set(TOOLING_DIR $ENV{HOME}/opt)

ExternalProject_Add(
	cmake
	PREFIX ${CMAKE_CURRENT_BINARY_DIR}
	GIT_REPOSITORY git://cmake.org/cmake.git
	GIT_TAG origin/next
	BUILD_IN_SOURCE 1
	#TEST_BEFORE_INSTALL 1
	CMAKE_ARGS -DCMAKE_INSTALL_PREFIX=${TOOLING_DIR}
	)

ExternalProject_Add(
	ninja	
	PREFIX ${CMAKE_CURRENT_BINARY_DIR}
	GIT_REPOSITORY https://github.com/martine/ninja.git
	GIT_TAG origin/master
	BUILD_IN_SOURCE 1
	CONFIGURE_COMMAND ""
	BUILD_COMMAND "./bootstrap.py"
	INSTALL_COMMAND cp ninja ${TOOLING_DIR}/bin/
	)

ExternalProject_Add(
	cppcheck
	PREFIX ${CMAKE_CURRENT_BINARY_DIR}
	GIT_REPOSITORY https://github.com/danmar/cppcheck.git
	GIT_TAG origin/master
	BUILD_IN_SOURCE 1
	CONFIGURE_COMMAND ""
	#TEST_BEFORE_INSTALL 1
	BUILD_COMMAND make -j ${NUMCPU} SRCDIR=build CFGDIR=${TOOLING_DIR}/bin/
	TEST_COMMAND make test
	INSTALL_COMMAND make PREFIX=${TOOLING_DIR} CFGDIR=${TOOLING_DIR}/bin/ install
	)

# Only download clang compiler-rt for use in llvm
set(COMPILERRT_SOURCE ${CMAKE_BINARY_DIR}/src/compiler-rt)
ExternalProject_Add(
	compiler-rt
	PREFIX ${CMAKE_CURRENT_BINARY_DIR}
	GIT_REPOSITORY http://llvm.org/git/compiler-rt.git
	GIT_TAG origin/master
	CONFIGURE_COMMAND ""
	BUILD_COMMAND ""
	INSTALL_COMMAND ""
	)

set(CLANG_SOURCE ${CMAKE_BINARY_DIR}/src/clang)
ExternalProject_Add(
	clang
	PREFIX ${CMAKE_CURRENT_BINARY_DIR}
	GIT_REPOSITORY http://llvm.org/git/clang.git
	GIT_TAG origin/master
	CONFIGURE_COMMAND ""
	BUILD_COMMAND ""
	INSTALL_COMMAND ""
	)

ExternalProject_Add(
	llvm
	PREFIX ${CMAKE_CURRENT_BINARY_DIR}
	GIT_REPOSITORY http://llvm.org/git/llvm.git
	GIT_TAG origin/master
	DEPENDS clang compiler-rt
	CMAKE_CACHE_ARGS 
		-DLLVM_INCLUDE_TOOLS:BOOL=ON
		-DLLVM_INSTALL_TOOLCHAIN_ONLY:BOOL=ON
		-DLLVM_TARGETS_TO_BUILD:STRING=X86;ARM
		-DLLVM_EXTERNAL_CLANG_SOURCE_DIR:PATH=${CLANG_SOURCE}
		-DLLVM_EXTERNAL_COMPILER_RT_SOURCE_DIR:PATH=${COMPILERRT_SOURCE}
		-DCMAKE_INSTALL_PREFIX:PATH=${TOOLING_DIR}
		-DCMAKE_BUILD_TYPE:STRING=Release
	)

ExternalProject_Add(
	astyle
	PREFIX ${CMAKE_CURRENT_BINARY_DIR}
	SVN_REPOSITORY https://svn.code.sf.net/p/astyle/code/trunk
	CONFIGURE_COMMAND ""
	BUILD_COMMAND make -j ${NUMCPU} -C ${CMAKE_CURRENT_BINARY_DIR}/src/astyle/AStyle/build/gcc/
	INSTALL_COMMAND make -C ${CMAKE_CURRENT_BINARY_DIR}/src/astyle/AStyle/build/gcc/ prefix=${TOOLING_DIR} install
	)

ExternalProject_Add(
	cpplint
	PREFIX ${CMAKE_CURRENT_BINARY_DIR}
	SVN_REPOSITORY http://google-styleguide.googlecode.com/svn/trunk
	CONFIGURE_COMMAND ""
	BUILD_COMMAND ""
	INSTALL_COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_BINARY_DIR}/src/cpplint/cpplint/cpplint.py ${TOOLING_DIR}/bin/
	)

ExternalProject_Add(
	vim	
	PREFIX ${CMAKE_CURRENT_BINARY_DIR}
	URL ftp://ftp.vim.org/pub/vim/unix/vim-7.4.tar.bz2
	CONFIGURE_COMMAND ./configure --disable-gui --prefix=${TOOLING_DIR}/ --with-features=huge --enable-pythoninterp --with-python-config-dir=/usr/lib/python2.7/config
	BUILD_COMMAND make -j${NUMCPU}
	INSTALL_COMMAND make install
	BUILD_IN_SOURCE 1
	)
