from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files, copy_metadata, get_package_paths
import os
import glob

pkg_base, pkg_dir = get_package_paths('paddle')
libs_dir = os.path.join(pkg_base, 'libs')

datas = collect_data_files('paddle')
binaries = []

if os.path.exists(libs_dir):
    for lib_file in glob.glob(os.path.join(libs_dir, '*.dylib')) + glob.glob(os.path.join(libs_dir, '*.so')):
        binaries.append((lib_file, 'paddle/libs'))

paddle_core_lib = os.path.join(pkg_base, 'libpaddle.so')
if os.path.exists(paddle_core_lib):
    binaries.append((paddle_core_lib, 'paddle'))

datas += copy_metadata('paddle')