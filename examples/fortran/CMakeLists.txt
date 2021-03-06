# (C) Copyright 2011- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

cmake_minimum_required( VERSION 3.6 FATAL_ERROR )

find_package( ecbuild REQUIRED )
project( compute_circle VERSION 0.10.0 LANGUAGES Fortran )

### options

ecbuild_add_option( FEATURE AREA_COMPUTER
                    DESCRIPTION "Wether we should build the area_computer executable" )

### lib const

ecbuild_add_library(
    TARGET  const
    TYPE    STATIC
    SOURCES constants.f90
    )

### lib area_circle

ecbuild_list_add_pattern( LIST area_srcs GLOB "*.f*" )

ecbuild_list_exclude_pattern( LIST area_srcs REGEX old.*f90 ^const.* .*f95 main.[fF]90 api/* )

ecbuild_generate_fortran_interfaces(

    TARGET      intf_circ

    SOURCE_DIR  ${CMAKE_CURRENT_SOURCE_DIR}

    DIRECTORIES api/area api/volume

    DESTINATION  api
)

ecbuild_add_library(

    TARGET  api_objs

    TYPE    OBJECT

    SOURCES_GLOB  "api/area/*.F90" "api/volume/*.F90"
)

ecbuild_add_library(
    TARGET      area_circle
    SOURCES     ${area_srcs}
    OBJECTS     api_objs
    PUBLIC_LIBS const intf_circ
)

# application conditionally compiled

ecbuild_add_executable(
    TARGET  area_computer
    SOURCES main.F90
    LIBS area_circle
    CONDITION HAVE_AREA_COMPUTER
    )

### finalize project

ecbuild_pkgconfig(
    NAME area_circle
    DESCRIPTION "A library to compute the area of a circle"
    LIBRARIES area_circle
    )

ecbuild_install_project( NAME ${PROJECT_NAME} )

ecbuild_print_summary()
