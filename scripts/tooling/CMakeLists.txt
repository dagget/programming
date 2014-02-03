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
	BUILD_IN_SOURCE 1
	CONFIGURE_COMMAND ""
	BUILD_COMMAND "./bootstrap.py"
	INSTALL_COMMAND cp ninja ${TOOLING_DIR}/bin/
	)

ExternalProject_Add(
	cppcheck
	PREFIX ${CMAKE_CURRENT_BINARY_DIR}
	GIT_REPOSITORY https://github.com/danmar/cppcheck.git
	BUILD_IN_SOURCE 1
	CONFIGURE_COMMAND ""
	BUILD_COMMAND make -j ${NUMCPU} SRCDIR=build CFGDIR=cfg
	INSTALL_COMMAND make PREFIX=${TOOLING_DIR} install
	)
