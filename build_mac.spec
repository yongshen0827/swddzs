# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import (
    collect_submodules, collect_data_files, collect_dynamic_libs, collect_all
)

block_cipher = None

# ==================== 1. 隐藏导入（核心） ====================
hiddenimports = [
    # ----- Paddle 系列 -----
    'paddle', 'paddle.fluid', 'paddle.fluid.core', 'paddle.fluid.core_avx',
    'paddle.incubate', 'paddle.distributed', 'paddle.dataset',
    'paddle.fluid.io', 'paddle.fluid.layers', 'paddle.fluid.param_attr',
    'paddleocr', 'paddlex', 'scipy._cyutility',

    # ----- EasyOCR -----
    'easyocr', 'easyocr.model.model', 'easyocr.detection', 'easyocr.recognition',
    'easyocr.utils', 'easyocr.config', 'easyocr.craft_utils', 'easyocr.imgproc',

    # ----- PyTorch -----
    'torch', 'torchvision', 'torchvision._C', 'torchaudio',

    # ----- OpenCV -----
    'cv2', 'cv2.cv2', 'cv2.data',

    # ----- 科学计算库 -----
    'numpy', 'numpy.core._dtype_ctypes', 'numpy.random._examples',
    'scipy', 'scipy.special._ufuncs', 'scipy.linalg._fblas',
    'scipy.sparse.csgraph._validation',
    'sklearn', 'sklearn.utils._weight_vector', 'sklearn.neighbors._typedefs',
    'skimage', 'skimage.io._plugins',

    # ----- Web 框架 -----
    'uvicorn', 'uvicorn.loops', 'uvicorn.loops.auto',
    'uvicorn.protocols', 'uvicorn.protocols.http.auto',
    'fastapi', 'fastapi.openapi', 'fastapi.openapi.utils',
    'starlette', 'pydantic', 'pydantic.utils',

    # ----- 文档处理 -----
    'fitz', 'PyMuPDF', 'pdfplumber',
    'pdfminer', 'pdfminer.pdfparser', 'pdfminer.pdfdocument',
    'openpyxl', 'openpyxl.cell._writer',

    # ----- 通用工具 -----
    'yaml', 'lxml', 'lxml._elementpath', 'lxml.etree',
    'networkx', 'shapely', 'shapely.geometry',
    'visualdl', 'modelscope', 'pypdfium2', 'premailer', 'cssutils',
    'importlib_metadata', 'importlib_resources', 'typing_extensions',
    'babel.numbers', 'jinja2.ext',
    '_rapidfuzz_cpp', 'rapidfuzz',

    # ----- 修复 setuptools/_distutils_hack 缺失 -----
    '_distutils_hack',
    '_distutils_hack.override',
    'setuptools._distutils_hack',
    'setuptools._distutils_hack.override',
    'setuptools._distutils',
    'setuptools.command',
    'setuptools.command.build_ext',
    'setuptools.command.install',
    'setuptools.dist',
    'Cython',
    'Cython.Compiler',
    'Cython.Compiler.Main',
    'Cython.Compiler.Symtab',
    'Cython.Compiler.PyrexTypes',
    'Cython.Compiler.Code',
    'Cython.Utils',
]

# 自动收集子模块
hiddenimports += collect_submodules('paddleocr')
hiddenimports += collect_submodules('paddle')
hiddenimports += collect_submodules('paddlex')
hiddenimports += collect_submodules('easyocr')
hiddenimports += collect_submodules('torch')
hiddenimports += collect_submodules('torchvision')
hiddenimports += collect_submodules('cv2')
hiddenimports += collect_submodules('sklearn')
hiddenimports += collect_submodules('skimage')
hiddenimports += collect_submodules('scipy')
hiddenimports += collect_submodules('uvicorn')
hiddenimports += collect_submodules('fastapi')
hiddenimports += collect_submodules('modelscope')
hiddenimports += collect_submodules('visualdl')
hiddenimports += collect_submodules('setuptools')

hiddenimports = list(set(hiddenimports))

# ==================== 2. 数据文件（模型） ====================
datas = []
# 收集 Cython 的 Utility 文件
try:
    import Cython.Utils
    cython_utility_dir = os.path.join(os.path.dirname(Cython.__file__), 'Utility')
    if os.path.exists(cython_utility_dir):
        datas.append((cython_utility_dir, 'Cython/Utility'))
        print(f"✅ 已添加 Cython Utility 目录: {cython_utility_dir}")
except Exception as e:
    print(f"⚠️ 无法收集 Cython Utility: {e}")
    
home = os.path.expanduser('~')
paddle_model_dir = os.path.join(home, '.paddleocr')
if os.path.exists(paddle_model_dir):
    datas.append((paddle_model_dir, '.paddleocr'))
    print(f"✅ 已添加 PaddleOCR 模型: {paddle_model_dir}")

easy_model_dir = os.path.join(home, '.EasyOCR')
if os.path.exists(easy_model_dir):
    datas.append((easy_model_dir, '.EasyOCR'))
    print(f"✅ 已添加 EasyOCR 模型: {easy_model_dir}")

# 收集库自带的数据文件
datas += collect_data_files('paddleocr')
datas += collect_data_files('paddlex')
datas += collect_data_files('easyocr')
datas += collect_data_files('cv2')
datas += collect_data_files('torch')
datas += collect_data_files('sklearn')
datas += collect_data_files('pydantic')
datas += collect_data_files('setuptools')

# ==================== 3. 二进制动态库 ====================
binaries = []

binaries += collect_dynamic_libs('paddle')
binaries += collect_dynamic_libs('torch')
binaries += collect_dynamic_libs('cv2')
binaries += collect_dynamic_libs('numpy')
binaries += collect_dynamic_libs('scipy')
binaries += collect_dynamic_libs('PIL')
binaries += collect_dynamic_libs('sklearn')
binaries += collect_dynamic_libs('skimage')
binaries += collect_dynamic_libs('shapely')
binaries += collect_dynamic_libs('lxml')
binaries += collect_dynamic_libs('fitz')
binaries += collect_dynamic_libs('rapidfuzz')

# 手动添加 Paddle 的 libs 目录
try:
    import paddle
    paddle_libs_dir = os.path.join(os.path.dirname(paddle.__file__), 'libs')
    if os.path.exists(paddle_libs_dir):
        binaries.append((paddle_libs_dir, '.'))
        print(f"✅ 已添加 Paddle 动态库目录: {paddle_libs_dir}")
except Exception as e:
    print(f"⚠️ 无法定位 Paddle 动态库目录: {e}")

# ==================== 4. 彻底解决 pkg_resources/jaraco 缺失 ====================
pkg_resources_all = collect_all('pkg_resources')
datas += pkg_resources_all[0]
binaries += pkg_resources_all[1]
hiddenimports += pkg_resources_all[2]

setuptools_all = collect_all('setuptools')
datas += setuptools_all[0]
binaries += setuptools_all[1]
hiddenimports += setuptools_all[2]

hiddenimports = list(set(hiddenimports))

# ==================== 5. 排除项 ====================
excludes = [
    'tkinter', 'test', 'unittest', 'pytest', 'setuptools', 'pip',
    'IPython', 'jupyter', 'notebook', 'matplotlib.tests',
    'numpy.random._examples', 'pandas.tests',
    'torch.cuda', 'torch.distributed',
]

# ==================== 6. Analysis ====================
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ==================== 7. EXE ====================
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
    target_arch='x86_64',
    codesign_identity=None,
    entitlements_file=None,
)

# ==================== 8. COLLECT ====================
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

# ==================== 9. BUNDLE ====================
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
        'NSAppleEventsUsageDescription': 'This app needs to control other applications to automate OCR tasks.',
    },
)
