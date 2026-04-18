# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs

block_cipher = None

# ---------- 1. 隐藏导入（针对 PaddleOCR / EasyOCR / 科学计算库）----------
hiddenimports = [
    # Paddle 系列
    'paddle', 'paddleocr', 'paddlex',
    'paddle.fluid', 'paddle.fluid.core', 'paddle.fluid.core_avx',
    'paddle.incubate', 'paddle.distributed', 'paddle.dataset',
    # EasyOCR
    'easyocr', 'easyocr.model.model', 'easyocr.detection', 'easyocr.recognition',
    'easyocr.utils', 'easyocr.config', 'easyocr.craft_utils', 'easyocr.imgproc',
    # OpenCV & 图像处理
    'cv2', 'cv2.cv2', 'cv2.data',
    # 科学计算
    'sklearn', 'sklearn.utils._weight_vector', 'sklearn.neighbors._typedefs',
    'skimage', 'scipy.special._ufuncs', 'scipy.linalg._fblas',
    'scipy.sparse.csgraph._validation',
    # Web 框架
    'uvicorn.loops', 'uvicorn.loops.auto', 'uvicorn.protocols', 'uvicorn.protocols.http.auto',
    'fastapi.openapi', 'fastapi.openapi.utils', 'starlette', 'pydantic',
    # 文档处理
    'pdfminer', 'pdfminer.pdfparser', 'pdfminer.pdfdocument', 'pdfplumber', 'fitz',
    # 通用工具
    'yaml', 'lxml.etree', 'networkx', 'shapely', 'visualdl', 'modelscope',
    'pypdfium2', 'premailer', 'cssutils', 'importlib_metadata', 'importlib_resources',
    'pkg_resources', 'typing_extensions', 'babel.numbers', 'jinja2.ext',
]

# 使用工具函数自动收集子模块（减少遗漏）
hiddenimports += collect_submodules('paddleocr')
hiddenimports += collect_submodules('paddle')
hiddenimports += collect_submodules('easyocr')
hiddenimports += collect_submodules('torch')
hiddenimports = list(set(hiddenimports))  # 去重

# ---------- 2. 数据文件（OCR 模型）----------
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
datas += collect_data_files('easyocr')
datas += collect_data_files('cv2')
datas += collect_data_files('torch')
datas += collect_data_files('sklearn')

# ---------- 3. 动态库 ----------
binaries = []
binaries += collect_dynamic_libs('paddle')
binaries += collect_dynamic_libs('torch')
binaries += collect_dynamic_libs('cv2')
binaries += collect_dynamic_libs('numpy')
binaries += collect_dynamic_libs('scipy')
binaries += collect_dynamic_libs('PIL')
binaries += collect_dynamic_libs('sklearn')
binaries += collect_dynamic_libs('skimage')

# ---------- 4. 排除项 ----------
excludes = ['tkinter', 'test', 'unittest', 'pytest', 'setuptools', 'pip',
            'IPython', 'jupyter', 'notebook', 'matplotlib.tests']

# ---------- 5. Analysis ----------
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

# ---------- 6. EXE ----------
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='main',                     # 内部可执行文件名，使用英文避免路径问题
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x86_64',            # 关键：指定 x86_64 架构
    codesign_identity=None,
    entitlements_file=None,
)

# ---------- 7. COLLECT ----------
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OrderAuditApp',            # 内部收集目录名，英文
)

# ---------- 8. BUNDLE（生成 .app）----------
app = BUNDLE(
    coll,
    name='商委订单审核助手服务端.app',   # 最终用户看到的 .app 名称
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
