cmake_minimum_required(VERSION 3.10)
if(${CMAKE_VERSION} VERSION_GREATER_EQUAL "3.13") 
    # policy introduced in CMake 3.13
    cmake_policy(SET CMP0078 OLD)
endif()
if(${CMAKE_VERSION} VERSION_GREATER_EQUAL "3.14") 
    # policy introduced in CMake 3.13
    cmake_policy(SET CMP0086 OLD)
endif()
project(python-libsnark)

include(cmake/libsnark.cmake)

add_subdirectory(depends)

#find_package (Python3 COMPONENTS Interpreter Development)

find_package(PythonInterp 3.5 REQUIRED)
find_package(PythonLibs 3.5 REQUIRED)

# need this for ${PYTHON_EXTENSION_MODULE_SUFFIX} -- actually this determines the
# suffix for the system python, not for python3...
include(cmake/FindPythonExtensions.cmake)

find_package(SWIG)
include(UseSWIG)

set_property(SOURCE libsnark.i PROPERTY CPLUSPLUS ON)

# TODO set additional dependencies
# TODO set swig builtin flag
swig_add_library(libsnark
                 TYPE SHARED
                 LANGUAGE python
                 SOURCES libsnark.i)

include_directories(${DEPENDS_DIR}/libsnark ${DEPENDS_DIR}/libsnark;${DEPENDS_DIR}/libsnark/depends/libfqfft;${DEPENDS_DIR}/libsnark/depends/libff;${OPENSSL_INCLUDE_DIR};${PYTHON_INCLUDE_DIRS};${GMP_INCLUDE_DIR})
set_property(TARGET ${SWIG_MODULE_libsnark_REAL_NAME} PROPERTY SUFFIX "${PYTHON_EXTENSION_MODULE_SUFFIX}")

#set_property(TARGET ${SWIG_MODULE_libsnark_REAL_NAME} PROPERTY SWIG_GENERATED_INCLUDE_DIRECTORIES )

#add_library(libsnark MODULE libsnark.cpp)
#python_extension_module(libsnark)
    
swig_link_libraries(libsnark snark ${PYTHON_LIBRARIES})


#target_include_directories(
#  libsnark
#
#  PUBLIC
#  ${DEPENDS_DIR}/libsnark
#  ${DEPENDS_DIR}/libsnark/depends/libfqfft
#  ${DEPENDS_DIR}/libsnark/depends/libff  
#  ${OPENSSL_INCLUDE_DIR}
#)


