cmake_minimum_required(VERSION 3.20)

project(cnxt_ownership_rt LANGUAGES CXX)

add_library(cnxt_ownership_rt SHARED
  src/ownership_runtime.cpp
)

target_compile_features(cnxt_ownership_rt PUBLIC cxx_std_17)

target_include_directories(cnxt_ownership_rt
  PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

set_target_properties(cnxt_ownership_rt PROPERTIES
  OUTPUT_NAME "cnxt_ownership_rt"
  VERSION "1.0.0"
  SOVERSION "1"
)
