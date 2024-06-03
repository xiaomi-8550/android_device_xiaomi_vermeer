#
# Copyright (C) 2024 Paranoid Android
#
# SPDX-License-Identifier: Apache-2.0
#

DEVICE_PATH := device/xiaomi/vermeer

# Inherit from sm8550-common
include device/xiaomi/sm8550-common/BoardConfigCommon.mk

# Display
TARGET_SCREEN_DENSITY := 530

# Kernel Modules
BOARD_VENDOR_RAMDISK_RECOVERY_KERNEL_MODULES_LOAD += goodix_ts.ko

# OTA
TARGET_OTA_ASSERT_DEVICE := vermeer

# Properties
TARGET_ODM_PROP += $(DEVICE_PATH)/configs/properties/odm.prop
