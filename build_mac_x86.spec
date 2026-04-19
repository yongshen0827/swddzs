# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import (
    collect_submodules, collect_data_files, collect_dynamic_libs, copy_metadata
)

block_cipher = None

# --- 1. 隐藏导入 ---
hiddenimports = [
    # Paddle & PaddleOCR 核心
    'paddle', 'paddleocr', 'paddlex',
    'paddle.fluid', 'paddle.base', 'paddle.dataset',
    'paddleocr._pipelines', 'paddleocr._pipelines.ocr',
    'paddlex.inference', 'paddlex.inference.pipelines',
    
    # PyTorch 核心
    'torch', 'torch.cuda',
    'torchvision', 'torchaudio',
    
    # EasyOCR
    'easyocr',
    
    # OpenCV
    'cv2',
    
    # Scipy 内部模块
    'scipy.special._ufuncs',
    'scipy.linalg.cython_blas',
    'scipy.linalg.cython_lapack',
    'scipy.sparse._csparsetools',
    
    # FastAPI & 工具
    'uvicorn', 'fastapi', 'pydantic', 'fitz', 'pdfplumber',
    'pkg_resources', 'pkg_resources._vendor', 'pkg_resources.extern',
    
    # modelscope
    'modelscope', 'addict',
    
    # jaraco 相关（解决 pkg_resources 依赖）
    'jaraco', 'jaraco.text',
]

# 自动收集子模块
hiddenimports += collect_submodules('paddleocr')
hiddenimports += collect_submodules('paddle')
hiddenimports += collect_submodules('paddlex')
hiddenimports += collect_submodules('torch')
hiddenimports += collect_submodules('modelscope')
hiddenimports += collect_submodules('sklearn')
# 🔥 关键：强制收集 jaraco 所有子模块
hiddenimports += collect_submodules('jaraco')
hiddenimports += collect_submodules('jaraco.text')
hiddenimports = list(set(hiddenimports))

# 移除明确不存在的模块
invalid_imports = [
    'paddleocr.tools', 'paddleocr.ppocr', 'paddleocr.ppstructure',
    'paddle.utils._cpp_infer', 'scipy._cyutility', 'importlib_resources.trees',
    'scipy._cyutility_cxx',
]
for inv in invalid_imports:
    if inv in hiddenimports:
        hiddenimports.remove(inv)

# --- 2. 数据文件 ---
datas = []
home = os.path.expanduser('~')
paddle_model_dir = os.path.join(home, '.paddleocr')
if os.path.exists(paddle_model_dir):
    datas.append((paddle_model_dir, '.paddleocr'))
easy_model_dir = os.path.join(home, '.EasyOCR')
if os.path.exists(easy_model_dir):
    datas.append((easy_model_dir, '.EasyOCR'))

datas += collect_data_files('paddleocr')
datas += collect_data_files('paddlex')
datas += collect_data_files('easyocr')
datas += collect_data_files('cv2')
datas += collect_data_files('torch')
datas += collect_data_files('sklearn')

# 🔥 额外收集 jaraco 的数据文件
try:
    datas += collect_data_files('jaraco')
    datas += collect_data_files('jaraco.text')
except:
    pass

# --- 3. 元数据收集 ---
metadata_datas = []
for pkg in ['paddlex', 'ftfy', 'imagesize', 'lxml', 'opencv-contrib-python',
            'openpyxl', 'pyclipper', 'modelscope', 'addict', 'torch', 'torchvision', 'torchaudio',
            'jaraco.text', 'jaraco']:
    try:
        metadata_datas += copy_metadata(pkg)
    except Exception as e:
        print(f"警告: 无法复制 {pkg} 的元数据: {e}")
datas += metadata_datas

# --- 4. 二进制动态库 ---
binaries = []
binaries += collect_dynamic_libs('paddle')
binaries += collect_dynamic_libs('torch')
binaries += collect_dynamic_libs('torchvision')
binaries += collect_dynamic_libs('torchaudio')
binaries += collect_dynamic_libs('cv2')
binaries += collect_dynamic_libs('numpy')
binaries += collect_dynamic_libs('scipy')
binaries += collect_dynamic_libs('PIL')
binaries += collect_dynamic_libs('sklearn')

# 手动收集 Paddle libs
try:
    import paddle
    paddle_libs_dir = os.path.join(os.path.dirname(paddle.__file__), 'libs')
    if os.path.exists(paddle_libs_dir):
        binaries.append((paddle_libs_dir, 'paddle/libs'))
        print(f"✅ 已收集 Paddle libs 目录: {paddle_libs_dir} -> paddle/libs")
except Exception as e:
    print(f"⚠️ 无法收集 Paddle libs 目录: {e}")

# 手动收集 Torch lib
try:
    import torch
    torch_lib_dir = os.path.join(os.path.dirname(torch.__file__), 'lib')
    if os.path.exists(torch_lib_dir):
        binaries.append((torch_lib_dir, 'torch/lib'))
        print(f"✅ 已收集 Torch lib 目录: {torch_lib_dir} -> torch/lib")
except Exception as e:
    print(f"⚠️ 无法收集 Torch lib 目录: {e}")

# --- 5. 排除项 ---
excludes = [
    'tkinter',
    'pytest',
    'setuptools',
    'pip',
    'IPython',
    'jupyter',
    'notebook',
    'matplotlib.tests',
    'paddle.tensorrt',
    'paddlex.inference.serving',
]

# --- 6. Analysis ---
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

# --- 7. EXE ---
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
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# --- 8. COLLECT ---
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

# --- 9. BUNDLE ---
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
