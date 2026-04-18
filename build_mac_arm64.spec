# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs

block_cipher = None

# ------------------------------------------------------------------
# 1. 收集所有隐藏导入（彻底穷举）
# ------------------------------------------------------------------
hiddenimports = []

# Paddle 系列
hiddenimports += collect_submodules('paddleocr')
hiddenimports += collect_submodules('paddle')
hiddenimports += collect_submodules('paddlex')
hiddenimports += [
    'paddle.fluid', 'paddle.fluid.core', 'paddle.fluid.core_avx',
    'paddle.incubate', 'paddle.distributed', 'paddle.dataset',
    'paddle.fluid.io', 'paddle.fluid.layers', 'paddle.fluid.param_attr',
]

# EasyOCR
hiddenimports += collect_submodules('easyocr')
hiddenimports += [
    'easyocr.model.model', 'easyocr.detection', 'easyocr.recognition',
    'easyocr.utils', 'easyocr.config', 'easyocr.craft_utils',
    'easyocr.imgproc',
]

# OpenCV
hiddenimports += collect_submodules('cv2')
hiddenimports += ['cv2.cv2', 'cv2.data']

# Torch
hiddenimports += collect_submodules('torch')
hiddenimports += collect_submodules('torchvision')

# 科学计算
hiddenimports += collect_submodules('sklearn')
hiddenimports += collect_submodules('skimage')
hiddenimports += collect_submodules('scipy')
hiddenimports += [
    'sklearn.utils._weight_vector', 'sklearn.neighbors._typedefs',
    'scipy.special._ufuncs', 'scipy.linalg._fblas',
    'scipy.sparse.csgraph._validation',
]

# Web 框架及工具
hiddenimports += [
    'uvicorn.loops', 'uvicorn.loops.auto',
    'uvicorn.protocols', 'uvicorn.protocols.http.auto',
    'fastapi.openapi', 'fastapi.openapi.utils',
    'pydantic', 'pydantic.utils',
    'pdfminer', 'pdfminer.pdfparser', 'pdfminer.pdfdocument',
    'pdfplumber', 'fitz', 'fitz.fitz',
    'PIL', 'PIL.Image', 'PIL.ImageDraw', 'PIL.ImageFont',
    'yaml', 'pkg_resources.py2_warn',
    'lxml', 'lxml.etree', 'networkx', 'shapely',
    'modelscope', 'visualdl', 'rarfile', 'pypdfium2',
    'premailer', 'cssutils', 'importlib_metadata',
    'importlib_resources', 'pkg_resources', 'typing_extensions',
    'dateutil', 'urllib3', 'certifi', 'charset_normalizer',
    'babel', 'babel.numbers', 'jinja2', 'jinja2.ext',
]

# 去重
hiddenimports = list(set(hiddenimports))

# ------------------------------------------------------------------
# 2. 收集数据文件（模型文件）
# ------------------------------------------------------------------
datas = []

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
datas += collect_data_files('easyocr')
datas += collect_data_files('cv2')
datas += collect_data_files('paddle')
datas += collect_data_files('torch')
datas += collect_data_files('sklearn')
datas += collect_data_files('pydantic')

# ------------------------------------------------------------------
# 3. 收集动态库（二进制文件）
# ------------------------------------------------------------------
binaries = []
binaries += collect_dynamic_libs('paddle')
binaries += collect_dynamic_libs('torch')
binaries += collect_dynamic_libs('cv2')
binaries += collect_dynamic_libs('numpy')
binaries += collect_dynamic_libs('scipy')
binaries += collect_dynamic_libs('PIL')
binaries += collect_dynamic_libs('sklearn')
binaries += collect_dynamic_libs('skimage')

# ------------------------------------------------------------------
# 4. 排除项
# ------------------------------------------------------------------
excludes = [
    'tkinter', 'test', 'unittest', 'pytest', 'setuptools', 'pip',
    'IPython', 'jupyter', 'notebook', 'matplotlib.tests',
    'numpy.random._examples', 'pandas.tests',
]

# ------------------------------------------------------------------
# 5. Analysis（主分析）
# ------------------------------------------------------------------
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

# ------------------------------------------------------------------
# 6. EXE（可执行文件，内部名称使用英文避免路径问题）
# ------------------------------------------------------------------
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='main',                     # 英文名，稳定可靠
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='arm64',             # 强制 ARM64
    codesign_identity=None,
    entitlements_file=None,
)

# ------------------------------------------------------------------
# 7. COLLECT（收集所有文件到目录）
# ------------------------------------------------------------------
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OrderAuditApp',            # 英文名，避免路径错误
)

# ------------------------------------------------------------------
# 8. BUNDLE（生成 macOS .app 包，显示名称为中文）
# ------------------------------------------------------------------
app = BUNDLE(
    coll,
    name='商委订单审核助手服务端.app',   # 最终显示给用户的名称
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
