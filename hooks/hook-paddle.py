from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files

# 收集 Paddle 的动态库
binaries = collect_dynamic_libs('paddle')
# 收集数据文件
datas = collect_data_files('paddle')

# 强制包含某些模块
hiddenimports = [
    'paddle.base.core',
    'paddle.utils._cpp_infer',
]
