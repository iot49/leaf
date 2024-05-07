#!/bin/bash

# based on micropython/tools/ci.sh

if which nproc > /dev/null; then
    MAKEOPTS="-j$(nproc)"
else
    MAKEOPTS="-j$(sysctl -n hw.ncpu)"
fi

# Ensure known OPEN_MAX (NO_FILES) limit.
ulimit -n 1024

########################################################################################
# ports/esp32

# GitHub tag of ESP-IDF to use for CI (note: must be a tag or a branch)
IDF_VER=v5.0.4

export IDF_CCACHE_ENABLE=1

function ci_esp32_idf_setup {
    echo ------ ci_esp32_idf_setup
    pip3 install pyelftools
    git clone --depth 1 --branch $IDF_VER https://github.com/espressif/esp-idf.git
    # doing a treeless clone isn't quite as good as --shallow-submodules, but it
    # is smaller than full clones and works when the submodule commit isn't a head.
    git -C esp-idf submodule update --init --recursive --filter=tree:0
    ./esp-idf/install.sh
}

function ci_esp32_build_common {
    echo ------ ci_esp32_build_common
    source tools/esp-idf/export.sh
    make ${MAKEOPTS} -C mpy-cross
    make ${MAKEOPTS} -C ports/esp32 submodules
}

function ci_esp32_build {
    echo ------ ci_esp32_build
    ci_esp32_idf_setup
    ci_esp32_build_common

    make ${MAKEOPTS} -C ports/esp32 \
        BOARD=ESP32_S3_N16R8
        # USER_C_MODULES=../../../examples/usercmodule/micropython.cmake \
        # FROZEN_MANIFEST=$(pwd)/ports/esp32/boards/manifest_test.py

}

function ci_esp32_build_cmod_spiram_s2 {
    ci_esp32_build_common

    make ${MAKEOPTS} -C ports/esp32 \
        USER_C_MODULES=../../../examples/usercmodule/micropython.cmake \
        FROZEN_MANIFEST=$(pwd)/ports/esp32/boards/manifest_test.py

    # Test building native .mpy with xtensawin architecture.
    ci_native_mpy_modules_build xtensawin

    make ${MAKEOPTS} -C ports/esp32 BOARD=ESP32_GENERIC BOARD_VARIANT=SPIRAM
    make ${MAKEOPTS} -C ports/esp32 BOARD=ESP32_GENERIC_S2
}

function ci_esp32_build_s3_c3 {
    ci_esp32_build_common

    make ${MAKEOPTS} -C ports/esp32 BOARD=ESP32_GENERIC_S3
    make ${MAKEOPTS} -C ports/esp32 BOARD=ESP32_GENERIC_C3
}
