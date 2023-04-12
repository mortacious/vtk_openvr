include(FetchContent)

set(proj VTK)
if (FETCH_${proj}_INSTALL_LOCATION)
  # The install location can be specified
  set(VTK_SOURCE_DIR "${FETCH_${proj}_INSTALL_LOCATION}")
else()
  set(VTK_SOURCE_DIR ${CMAKE_BINARY_DIR}/${proj})
endif()

FetchContent_Populate(${proj}
  SOURCE_DIR     ${VTK_SOURCE_DIR}
  GIT_REPOSITORY https://github.com/Kitware/VTK.git
  GIT_TAG        v${VTK_VERSION}
  QUIET
  )

message(STATUS "Remote - ${proj} [OK]")

set(VTK_SOURCE_DIR ${VTK_SOURCE_DIR})
message(STATUS "Remote - VTK_SOURCE_DIR:${VTK_SOURCE_DIR}")