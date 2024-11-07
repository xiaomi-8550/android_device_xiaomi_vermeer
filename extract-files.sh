#!/bin/bash
#
# SPDX-FileCopyrightText: 2016 The CyanogenMod Project
# SPDX-FileCopyrightText: 2017-2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

function blob_fixup() {
    case "${1}" in
        odm/etc/camera/aivsModel_6C06C006 | odm/lib64/libmialgo_aisn.so)
            [ "$2" = "" ] && return 0
            split --bytes=20M -d "${2}" "${2}".part
            ;;
        odm/etc/camera/enhance_motiontuning.xml |odm/etc/camera/night_motiontuning.xml | odm/etc/camera/motiontuning.xml)
            [ "$2" = "" ] && return 0
            sed -i 's/<?xml=/<?xml /g' "${2}"
            ;;
        odm/lib64/libailab_rawhdr.so | odm/lib64/libxmi_high_dynamic_range_cdsp.so)
            [ "$2" = "" ] && return 0
            "${ANDROID_ROOT}"/prebuilts/clang/host/linux-x86/clang-r450784e/bin/llvm-strip --strip-debug "${2}"
            ;;
        *)
            return 1
            ;;
    esac

    return 0
}

function blob_fixup_dry() {
    blob_fixup "$1" ""
}

# If we're being sourced by the common script that we called,
# stop right here. No need to go down the rabbit hole.
if [ "${BASH_SOURCE[0]}" != "${0}" ]; then
    return
fi

set -e

export DEVICE=vermeer
export DEVICE_COMMON=sm8550-common
export VENDOR=xiaomi
export VENDOR_COMMON=${VENDOR}

"./../../${VENDOR_COMMON}/${DEVICE_COMMON}/extract-files.sh" "$@"
