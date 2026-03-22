cmake_minimum_required(VERSION 3.20)

project(cnxt_ownership_rt LANGUAGES CXX)

include(CTest)

option(CNXT_OWNERSHIP_RT_ENABLE_SANITIZERS
  "Build the ownership runtime and smoke tests with AddressSanitizer/LeakSanitizer."
  OFF
)

if(CNXT_OWNERSHIP_RT_ENABLE_SANITIZERS
   AND NOT CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
  message(FATAL_ERROR
    "CNXT_OWNERSHIP_RT_ENABLE_SANITIZERS requires a Clang- or GCC-compatible compiler."
  )
endif()

set(CNXT_OWNERSHIP_RT_SANITIZER_COMPILE_FLAGS
  -fsanitize=address,leak
  -fno-omit-frame-pointer
)
set(CNXT_OWNERSHIP_RT_SANITIZER_LINK_FLAGS
  -fsanitize=address,leak
)

function(cnxt_ownership_apply_sanitizers target_name)
  if(NOT CNXT_OWNERSHIP_RT_ENABLE_SANITIZERS)
    return()
  endif()

  target_compile_options(${target_name} PRIVATE
    ${CNXT_OWNERSHIP_RT_SANITIZER_COMPILE_FLAGS}
  )
  target_link_options(${target_name} PRIVATE
    ${CNXT_OWNERSHIP_RT_SANITIZER_LINK_FLAGS}
  )
endfunction()

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

cnxt_ownership_apply_sanitizers(cnxt_ownership_rt)

if(BUILD_TESTING)
  add_executable(cnxt_ownership_rt_smoke
    tests/ownership_runtime_smoke.cpp
  )
  target_compile_features(cnxt_ownership_rt_smoke PRIVATE cxx_std_17)
  target_link_libraries(cnxt_ownership_rt_smoke PRIVATE cnxt_ownership_rt)
  cnxt_ownership_apply_sanitizers(cnxt_ownership_rt_smoke)

  add_test(
    NAME cnxt_ownership_rt.clean
    COMMAND cnxt_ownership_rt_smoke clean
  )

  add_test(
    NAME cnxt_ownership_rt.weak_lock_stress
    COMMAND cnxt_ownership_rt_smoke weak_lock_stress
  )

  if(CNXT_OWNERSHIP_RT_ENABLE_SANITIZERS)
    add_test(
      NAME cnxt_ownership_rt.use_after_free
      COMMAND
        ${CMAKE_COMMAND}
        -DTEST_COMMAND=$<TARGET_FILE:cnxt_ownership_rt_smoke>
        -DTEST_MODE=use_after_free
        -DASAN_OPTIONS=detect_leaks=0:abort_on_error=1
        -DEXPECT_SUBSTRING=ERROR:\ AddressSanitizer:\ heap-use-after-free
        -P ${CMAKE_CURRENT_SOURCE_DIR}/cmake/expect_sanitizer_failure.cmake
    )

    add_test(
      NAME cnxt_ownership_rt.double_free
      COMMAND
        ${CMAKE_COMMAND}
        -DTEST_COMMAND=$<TARGET_FILE:cnxt_ownership_rt_smoke>
        -DTEST_MODE=double_free
        -DASAN_OPTIONS=detect_leaks=1:abort_on_error=1
        -DEXPECT_SUBSTRING=ERROR:\ AddressSanitizer:\ attempting\ double-free
        -P ${CMAKE_CURRENT_SOURCE_DIR}/cmake/expect_sanitizer_failure.cmake
    )

    add_test(
      NAME cnxt_ownership_rt.leak
      COMMAND
        ${CMAKE_COMMAND}
        -DTEST_COMMAND=$<TARGET_FILE:cnxt_ownership_rt_smoke>
        -DTEST_MODE=leak
        -DASAN_OPTIONS=detect_leaks=1:abort_on_error=1
        -DEXPECT_SUBSTRING=ERROR:\ LeakSanitizer:\ detected\ memory\ leaks
        -P ${CMAKE_CURRENT_SOURCE_DIR}/cmake/expect_sanitizer_failure.cmake
    )
  endif()
endif()
