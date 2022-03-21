# we need cmake >= 3.11 so the FetchContent module is available
cmake_minimum_required(VERSION 3.11 FATAL_ERROR)
set_property(GLOBAL PROPERTY GLOBAL_DEPENDS_DEBUG_MODE 1)
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
set (CMAKE_CXX_STANDARD 17)
set(version 1.0)
project(vtkOpenVR)
set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR}/cmake)

option(BUILD_PYTHON "Build the python wrappers" OFF)
message(STATUS "Rpath is: ${CMAKE_INSTALL_RPATH}")

include(FetchContent)

set(VTK_COMPONENTS
        CommonCore
        IOImage
        IOXMLParser
        InteractionStyle
        InteractionWidgets
        RenderingOpenGL2
        RenderingVolumeOpenGL2
        vtksys
        CommonSystem
        FiltersSources
        IOXML
        ImagingSources
        glew
        opengl
        Python
        )

set(OpenVR_ROOT_DIR "${CMAKE_BINARY_DIR}/OPENVR")


# fetch the openVR library from it's github repository
FetchContent_Declare(
        openvr
        GIT_REPOSITORY https://github.com/ValveSoftware/openvr
        GIT_TAG master
        SOURCE_DIR "${OpenVR_ROOT_DIR}"
)
FetchContent_GetProperties(openvr)
if(NOT openvr_POPULATED)
    message(STATUS "Fetching source tree for OpenVR")
    FetchContent_Populate(openvr)
endif()

find_package(OpenVR REQUIRED)
# define a custom target for openvr
add_library(OpenVR::OpenVR SHARED IMPORTED)
set_target_properties(OpenVR::OpenVR PROPERTIES
        IMPORTED_LOCATION "${OpenVR_LIBRARIES}"
        INTERFACE_INCLUDE_DIRECTORIES "${OpenVR_INCLUDE_DIRS}"
        IMPORTED_NO_SONAME TRUE)
#set(OpenVR_ROOT "${OPENVR_ROOT_DIR}")

message(STATUS "OpenVR location ${OpenVR_LIBRARIES}")
# VTK dependency
find_package(VTK 9 REQUIRED
        COMPONENTS
        ${VTK_COMPONENTS}
        )

if(${VTK_VERSION} VERSION_LESS 9.0)
    message(FATAL_ERROR "VTK >= 9.0 is REQUIRED")
endif()

if(NOT TARGET VTK::RenderingOpenVR)


message(STATUS "Found VTK version ${VTK_VERSION}")
# the conda-forge VTK package seems to be broken and this is not really needed so just reset it
set_property(TARGET VTK::opengl PROPERTY INTERFACE_INCLUDE_DIRECTORIES)
set_property(TARGET VTK::opengl PROPERTY INTERFACE_LINK_LIBRARIES)
set_property(TARGET VTK::opengl PROPERTY INTERFACE_SYSTEM_INCLUDE_DIRECTORIES)

# fetch vtk to get the required openvr module sources
FetchContent_Declare(
        vtk
        GIT_REPOSITORY https://github.com/Kitware/VTK.git
        GIT_TAG v${VTK_MAJOR_VERSION}.${VTK_MINOR_VERSION}.${VTK_BUILD_VERSION}
        SOURCE_DIR "${CMAKE_BINARY_DIR}/VTK"
)
FetchContent_GetProperties(vtk)
if(NOT vtk_POPULATED)
    message(STATUS "Fetching source tree for VTK version ${VTK_MAJOR_VERSION}.${VTK_MINOR_VERSION}.${VTK_BUILD_VERSION}")
    FetchContent_Populate(vtk)
endif()

set(VTK_OPENVR_DIRECTORY ${CMAKE_BINARY_DIR}/VTK/Rendering/OpenVR)
set(VTK_VR_DIRECTORY ${CMAKE_BINARY_DIR}/VTK/Rendering/VR)


include(GNUInstallDirs)

set(_shared_default ON)
get_target_property(_vtk_libtype VTK::CommonCore TYPE)
if (_vtk_libtype STREQUAL "STATIC_LIBRARY")
    set(_shared_default OFF)
endif ()

option(BUILD_SHARED_LIBS "Build shared or static libraries" "${_shared_default}")

# First we scan the modules in our project to find out the dependency graph
# between them.
if(BUILD_PYTHON)
    message(STATUS "Building python module")
    set(OUTPUT_DIR "vtk_openvr/lib")
    set(INSTALL_HEADERS OFF)
    include_directories("${Python3_INCLUDE_DIR}")
else()
    set(OUTPUT_DIR ${LIBRARY_OUTPUT_DIRECTORY})
    set(INSTALL_HEADERS ON)
endif()
set(modules)

vtk_module_find_modules(this_modules "${CMAKE_CURRENT_SOURCE_DIR}/src")

if(${VTK_VERSION} VERSION_GREATER_EQUAL 9.1)
    # in VTK 9.1 the new RenderingVR module that might not be present so build it as well
    vtk_module_scan(
            # With only 1 module file, this is easier. With more,
            # `vtk_module_find_modules` would be preferred.
            MODULE_FILES      "${VTK_VR_DIRECTORY}/vtk.module"
            # Not building the only module we have is silly.
            REQUEST_MODULES   VTK::RenderingVR
            # Store the list of provided modules from this scan.
            PROVIDES_MODULES  vr_modules
            # Enable the tests for our modules.
            ENABLE_TESTS      OFF
    )
    list(APPEND modules ${vr_modules})
endif()

vtk_module_scan(
        # With only 1 module file, this is easier. With more,
        # `vtk_module_find_modules` would be preferred.
        MODULE_FILES      "${VTK_OPENVR_DIRECTORY}/vtk.module"
        # Not building the only module we have is silly.
        REQUEST_MODULES   VTK::RenderingOpenVR
        # Store the list of provided modules from this scan.
        PROVIDES_MODULES  openvr_modules
        # Enable the tests for our modules.
        ENABLE_TESTS      OFF
)
list(APPEND modules ${openvr_modules})


message(STATUS "Building modules ${modules}")
#set("${CMAKE_PROJECT_NAME}Targets"
#        EXPORT "${CMAKE_PROJECT_NAME}Targets")

# Build the module we just scanned.
vtk_module_build(
        MODULES ${modules}
        LIBRARY_DESTINATION "${OUTPUT_DIR}"
        INSTALL_HEADERS ${INSTALL_HEADERS}
        INSTALL_EXPORT "vtkopenvr"
        )

if(BUILD_PYTHON)
    # unset the property that associates the openvr package with the default vtk python package
    #set_property(TARGET VTK::RenderingOpenVR PROPERTY INTERFACE_vtk_module_python_package)

    # Wrap it with Python.
    vtk_module_wrap_python(
            MODULES         ${modules}
            PYTHON_PACKAGE  "vtk_openvr"
            MODULE_DESTINATION "."
            LIBRARY_DESTINATION "${OUTPUT_DIR}"
            # Static Python modules are almost never wanted.
            BUILD_STATIC    OFF
            INSTALL_HEADERS OFF)
    # copy the openvr library to the install location for python
    file(COPY "${OpenVR_LIBRARIES}" DESTINATION "${CMAKE_INSTALL_PREFIX}/vtk_openvr/lib")
else()
    include(CMakePackageConfigHelpers)
    set(INCLUDE_INSTALL_DIR "include/")

    install(EXPORT vtkopenvr
            FILE "vtkopenvr-targets.cmake"
            NAMESPACE ${CMAKE_PROJECT_NAME}::
            DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/${CMAKE_PROJECT_NAME})

    configure_package_config_file("vtkopenvr-config.cmake.in"
            "${CMAKE_BINARY_DIR}/vtkopenvr-config.cmake"
            INSTALL_DESTINATION lib/cmake
            PATH_VARS INCLUDE_INSTALL_DIR
            )

    write_basic_package_version_file(
            "${CMAKE_BINARY_DIR}/vtkopenvr-config-version.cmake"
            VERSION 0.1.0
            COMPATIBILITY AnyNewerVersion
    )

    install(
            FILES
            "${CMAKE_BINARY_DIR}/vtkopenvr-config.cmake"
            "${CMAKE_BINARY_DIR}/vtkopenvr-config-version.cmake"
            DESTINATION lib/cmake/${CMAKE_PROJECT_NAME}
    )
    #set(CMAKE_INSTALL_RPATH ".")
    #message(STATUS "Rpath is: ${CMAKE_INSTALL_RPATH}")
    # put the openvr library at vtk-openvr's location
    install(FILES "${OpenVR_LIBRARIES}" DESTINATION lib)
endif()

else()
    message(WARNING "The VTK::RenderingOpenVR module is already present in the local vtk installation! Due to restrictions in the vtk build system
    this module cannot be built with the same module already installed. The python package will fall back to the installed module.")

    if(BUILD_PYTHON)
        add_custom_target(vtkRenderingOpenVRPython)
    endif()
endif()


