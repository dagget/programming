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
	BUILD_COMMAND make -j ${NUMCPU} SRCDIR=build CFGDIR=cfg
	INSTALL_COMMAND make PREFIX=${TOOLING_DIR} install
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
	)
