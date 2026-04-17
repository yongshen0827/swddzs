# hook-paddle.py
# 规范的 PyInstaller 钩子文件，用于收集 PaddlePaddle 的动态库

from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files, copy_metadata, get_package_paths
import os
import glob

# 获取 paddle 包的安装路径
pkg_base, pkg_dir = get_package_paths('paddle')
libs_dir = os.path.join(pkg_base, 'libs')

# 收集数据文件
datas = collect_data_files('paddle')

# 收集动态库（macOS 关注 .dylib 和 .so）
binaries = []
if os.path.exists(libs_dir):
    for lib_file in glob.glob(os.path.join(libs_dir, '*.dylib')) + glob.glob(os.path.join(libs_dir, '*.so')):
        binaries.append((lib_file, 'paddle/libs'))

# 收集可能遗漏的核心库
paddle_core_lib = os.path.join(pkg_base, 'libpaddle.so')
if os.path.exists(paddle_core_lib):
    binaries.append((paddle_core_lib, 'paddle'))

# 收集元数据
datas += copy_metadata('paddle')
