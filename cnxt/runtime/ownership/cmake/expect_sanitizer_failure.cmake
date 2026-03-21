if(NOT DEFINED TEST_COMMAND)
  message(FATAL_ERROR "TEST_COMMAND must be set.")
endif()

if(NOT DEFINED TEST_MODE)
  message(FATAL_ERROR "TEST_MODE must be set.")
endif()

if(NOT DEFINED EXPECT_SUBSTRING)
  message(FATAL_ERROR "EXPECT_SUBSTRING must be set.")
endif()

if(NOT DEFINED ASAN_OPTIONS)
  set(ASAN_OPTIONS "detect_leaks=1:abort_on_error=1")
endif()

execute_process(
  COMMAND
    ${CMAKE_COMMAND} -E env
    ASAN_OPTIONS=${ASAN_OPTIONS}
    ${TEST_COMMAND}
    ${TEST_MODE}
  RESULT_VARIABLE TEST_RESULT
  OUTPUT_VARIABLE TEST_STDOUT
  ERROR_VARIABLE TEST_STDERR
)

if("${TEST_RESULT}" STREQUAL "0")
  message(FATAL_ERROR
    "Expected sanitizer failure for '${TEST_MODE}', but the test exited successfully."
  )
endif()

string(CONCAT TEST_OUTPUT "${TEST_STDOUT}" "${TEST_STDERR}")
string(FIND "${TEST_OUTPUT}" "${EXPECT_SUBSTRING}" MATCH_OFFSET)
if(MATCH_OFFSET EQUAL -1)
  message(FATAL_ERROR
    "Expected sanitizer output '${EXPECT_SUBSTRING}' was not found.\n${TEST_OUTPUT}"
  )
endif()
