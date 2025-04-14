#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

import os
import stat
from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)
from extract_utils.utils import (
    Color,
    color_print,
)

namespace_imports = [
    'vendor/xiaomi/sm8550-common',
    'vendor/qcom/common/vendor/adreno-t',
    'vendor/qcom/common/vendor/display/5.15',
]

def lib_fixup_odm_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_odm' if partition in ('odm', 'vendor') else None

lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    (
        'sqlite3',
        'vendor.xiaomi.hardware.fx.tunnel@1.0',
    ): lib_fixup_odm_suffix,
}

def blob_fixup_split_file(
    ctx: 'BlobFixupCtx',
    file: 'File',
    file_path: str,
    *args,
    **kwargs,
):
    # Split the file into parts
    part_size = 51380224 # 49 MiB
    part_number = 0
    with open(file_path, 'rb') as f:
        while chunk := f.read(part_size):
            part_file_name = f"{file_path}.part{part_number:02d}"
            with open(part_file_name, 'wb') as part_file:
                part_file.write(chunk)
            part_number += 1
    color_print(f'{file.dst}: split into {part_number} parts', color=Color.GREEN)

    # Add the file to .gitignore
    gitignore_path = os.path.join(module.vendor_path, '.gitignore')
    with open(gitignore_path, 'a+') as gitignore_file:
        gitignore_file.seek(0)  # Move to the start of the file
        existing_entries = gitignore_file.read().splitlines()
        if f'proprietary/{file.dst}' not in existing_entries:
            gitignore_file.write(f'proprietary/{file.dst}\n')
            color_print(f'{file.dst}: added to .gitignore', color=Color.GREEN)

blob_fixups: blob_fixups_user_type = {
    (
        'odm/etc/camera/aivsModel_6C06C006',
        'odm/lib64/libmialgo_aisn.so',
    ): blob_fixup()
        .call(blob_fixup_split_file),
    (
        'odm/etc/camera/enhance_motiontuning.xml',
        'odm/etc/camera/night_motiontuning.xml',
        'odm/etc/camera/motiontuning.xml',
    ): blob_fixup()
        .regex_replace(
            'xml=version',
            'xml version',
        ),
    (
        'odm/lib64/libailab_rawhdr.so',
        'odm/lib64/libxmi_high_dynamic_range_cdsp.so',
    ): blob_fixup()
        .strip_debug_sections(),
    'odm/lib64/libwrapper_dlengine.so': blob_fixup()
        .add_needed('liblog.so'),
}

module = ExtractUtilsModule(
    'vermeer',
    'xiaomi',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
)

def generate_vendorsetup_script():
    vendorsetup_path = os.path.join(module.vendor_path, "vendorsetup.sh")
    with open(vendorsetup_path, 'w') as setup_file:
        setup_file.write('#!/bin/bash\n')
        setup_file.write('# Script to dynamically reassemble .part* files\n\n')
        setup_file.write(f'for file in $(find \"{module.vendor_rel_path}\" -type f -name \"*.part00\"); do\n')
        setup_file.write('    base_name=${file%.part00}\n')
        setup_file.write('    cat ${base_name}.part* > $base_name\n')
        setup_file.write('    echo \"Reassembly of $base_name complete!\"\n')
        setup_file.write('done\n')
    os.chmod(vendorsetup_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    color_print(f'Generated dynamic reassembly script: vendorsetup.sh', color=Color.END)

if __name__ == '__main__':
    utils = ExtractUtils.device_with_common(
        module, 'sm8550-common', module.vendor
    )
    utils.run()
    generate_vendorsetup_script()
