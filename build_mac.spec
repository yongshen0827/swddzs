# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import platform
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs

block_cipher = None

# --- 1. 动态库与隐藏导入配置 (适配 PaddleOCR 3.x) ---
hiddenimports = [
    # Paddle 和 PaddleOCR 核心模块 (3.x)
    'paddle', 'paddleocr', 'paddlex',
    'paddle.fluid', 'paddle.base', 'paddle.dataset',
    # 重点: 补全 PaddleOCR 3.x 新架构下的内部模块
    'paddleocr.tools', 'paddleocr.ppocr', 'paddleocr.ppstructure',
    # 其他关键依赖
    'easyocr', 'cv2', 'sklearn', 'skimage',
    'scipy._cyutility', 'scipy.special._ufuncs',
    'uvicorn', 'fastapi', 'pydantic', 'fitz', 'pdfplumber',
    # 处理 setuptools / pkg_resources 的潜在缺失
    'pkg_resources', 'pkg_resources._vendor', 'pkg_resources.extern',
]

# 自动收集子模块，防止遗漏
hiddenimports += collect_submodules('paddleocr')
hiddenimports += collect_submodules('paddle')
hiddenimports += collect_submodules('paddlex')
hiddenimports = list(set(hiddenimports))

# --- 2. 数据文件 (模型) ---
datas = []
home = os.path.expanduser('~')
paddle_model_dir = os.path.join(home, '.paddleocr')
if os.path.exists(paddle_model_dir):
    datas.append((paddle_model_dir, '.paddleocr'))
easy_model_dir = os.path.join(home, '.EasyOCR')
if os.path.exists(easy_model_dir):
    datas.append((easy_model_dir, '.EasyOCR'))

# 收集库自带的数据文件
datas += collect_data_files('paddleocr')
datas += collect_data_files('paddlex')
datas += collect_data_files('easyocr')
datas += collect_data_files('cv2')
datas += collect_data_files('torch')
datas += collect_data_files('sklearn')

# --- 3. 二进制动态库 (核心: 解决 "Illegal instruction") ---
binaries = []
# 显式收集 Paddle 和 Torch 的动态库，确保指令集兼容的版本被正确打包
binaries += collect_dynamic_libs('paddle')
binaries += collect_dynamic_libs('torch')
binaries += collect_dynamic_libs('cv2')
binaries += collect_dynamic_libs('numpy')
binaries += collect_dynamic_libs('scipy')
binaries += collect_dynamic_libs('PIL')
binaries += collect_dynamic_libs('sklearn')

# 手动添加 Paddle 的 libs 目录，以防万一
try:
    import paddle
    paddle_libs_dir = os.path.join(os.path.dirname(paddle.__file__), 'libs')
    if os.path.exists(paddle_libs_dir):
        binaries.append((paddle_libs_dir, '.'))
except Exception:
    pass

# --- 4. 排除项 (减小体积) ---
excludes = [
    'tkinter', 'test', 'unittest', 'pytest', 'setuptools', 'pip',
    'IPython', 'jupyter', 'notebook', 'matplotlib.tests',
    'torch.cuda', 'torch.distributed',
]

# --- 5. Analysis (主分析) ---
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# --- 6. EXE (可执行文件) ---
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='arm64',
    codesign_identity=None,
    entitlements_file=None,
)

# --- 7. COLLECT (收集文件夹) ---
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OrderAuditApp',
)

# --- 8. BUNDLE (生成 .app) ---
app = BUNDLE(
    coll,
    name='商委订单审核助手服务端.app',
    icon=None,
    bundle_identifier='com.shangwei.order.audit',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'LSMinimumSystemVersion': '11.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundleSupportedPlatforms': ['MacOSX'],
        'DTPlatformName': 'macosx',
    },
)

# 增加隐式导入
hiddenimports = [
    # ... (原有模块) ...
    'paddle.base.libpaddle',
    'paddle.utils.cpp_extension.loader',
    'scipy.linalg.cython_blas',
    'scipy.linalg.cython_lapack',
    'scipy.sparse._csparsetools',
]
