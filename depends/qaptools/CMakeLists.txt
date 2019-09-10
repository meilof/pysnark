project(qaptools)
cmake_minimum_required(VERSION 3.1)
set (CMAKE_CXX_STANDARD 11)

find_path(GMP_INCLUDE_DIR NAMES gmp.h)
find_library(GMP_LIBRARIES NAMES gmp libgmp)
find_library(GMPXX_LIBRARIES NAMES gmpxx libgmpxx)
include_directories(${GMP_INCLUDE_DIR})

include_directories(depends/ate-pairing/include)
include_directories(depends/xbyak)

add_definitions(-DBN_SUPPORT_SNARK=1)

add_library(
    zm
    STATIC

    depends/ate-pairing/src/zm.cpp
    depends/ate-pairing/src/zm2.cpp
)

add_library(
    qap
    STATIC

    key.cpp
    proof.cpp
    modp.cpp
    base.cpp
    qap2key.cpp
    fft.cpp
    prove.cpp
    qap.cpp
    verify.cpp
)

link_libraries(qap zm ${GMP_LIBRARIES} ${GMPXX_LIBRARIES})

add_executable(qapgen qapgen.cpp)
add_executable(qapcoeffcache qapcoeffcache.cpp)
add_executable(qapgenf qapgenf.cpp)
add_executable(qapinput qapinput.cpp)
add_executable(qapprove qapprove.cpp)
add_executable(qapver qapver.cpp)
