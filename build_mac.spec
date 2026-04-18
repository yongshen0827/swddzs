# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs, copy_metadata

block_cipher = None

# ==================== 1. 隐藏导入（核心） ====================
hiddenimports = [
    # ----- Paddle 系列（OCR核心）-----
    'paddle', 'paddle.fluid', 'paddle.fluid.core', 'paddle.fluid.core_avx',
    'paddle.incubate', 'paddle.distributed', 'paddle.dataset',
    'paddle.fluid.io', 'paddle.fluid.layers', 'paddle.fluid.param_attr',
    'paddleocr', 'paddlex', 'scipy._cyutility',

    # ----- EasyOCR（备用）-----
    'easyocr', 'easyocr.model.model', 'easyocr.detection', 'easyocr.recognition',
    'easyocr.utils', 'easyocr.config', 'easyocr.craft_utils', 'easyocr.imgproc',

    # ----- PyTorch（EasyOCR 依赖）-----
    'torch', 'torchvision', 'torchvision._C', 'torchaudio',

    # ----- OpenCV（图像处理）-----
    'cv2', 'cv2.cv2', 'cv2.data',

    # ----- 科学计算库-----
    'numpy', 'numpy.core._dtype_ctypes', 'numpy.random._examples',
    'scipy', 'scipy.special._ufuncs', 'scipy.linalg._fblas',
    'scipy.sparse.csgraph._validation', 'scipy._cyutility',
    'sklearn', 'sklearn.utils._weight_vector', 'sklearn.neighbors._typedefs',
    'skimage', 'skimage.io._plugins',

    # ----- Web 框架（FastAPI + Uvicorn）-----
    'uvicorn', 'uvicorn.loops', 'uvicorn.loops.auto',
    'uvicorn.protocols', 'uvicorn.protocols.http.auto',
    'fastapi', 'fastapi.openapi', 'fastapi.openapi.utils',
    'starlette', 'pydantic', 'pydantic.utils',

    # ----- 文档处理（PDF + Excel）-----
    'fitz', 'PyMuPDF', 'pdfplumber',
    'pdfminer', 'pdfminer.pdfparser', 'pdfminer.pdfdocument',
    'openpyxl', 'openpyxl.cell._writer',

    # ----- 通用工具库-----
    'yaml', 'lxml', 'lxml._elementpath', 'lxml.etree',
    'networkx', 'shapely', 'shapely.geometry',
    'visualdl', 'modelscope', 'pypdfium2', 'premailer', 'cssutils',
    'importlib_metadata', 'importlib_resources', 'typing_extensions',
    'babel.numbers', 'jinja2.ext',
    '_rapidfuzz_cpp', 'rapidfuzz',

    # ----- 修复 jaraco/pkg_resources 缺失（上次崩溃的根源）-----
    'pkg_resources',
    'pkg_resources.py2_warn',
    'pkg_resources._vendor',
    'pkg_resources._vendor.jaraco',
    'pkg_resources._vendor.jaraco.functools',
    'pkg_resources._vendor.jaraco.context',
    'pkg_resources._vendor.jaraco.text',
    'pkg_resources._vendor.more_itertools',
    'pkg_resources._vendor.packaging',
    'pkg_resources.extern',
    'jaraco',
    'jaraco.functools',
    'jaraco.context',
    'jaraco.text',
]

# 自动收集子模块（减少手动遗漏）
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
hiddenimports += collect_submodules('pkg_resources._vendor')

hiddenimports = list(set(hiddenimports))  # 去重

# ==================== 2. 数据文件（模型 + 元数据） ====================
datas = []

# 打包 PaddleOCR 模型目录
home = os.path.expanduser('~')
paddle_model_dir = os.path.join(home, '.paddleocr')
if os.path.exists(paddle_model_dir):
    datas.append((paddle_model_dir, '.paddleocr'))
    print(f"✅ 已添加 PaddleOCR 模型: {paddle_model_dir}")

# 打包 EasyOCR 模型目录
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

# 复制元数据（PaddleX 运行时检查依赖时需要）[reference:13]
datas += copy_metadata('ftfy')
datas += copy_metadata('imagesize')
datas += copy_metadata('lxml')
datas += copy_metadata('opencv-contrib-python')
datas += copy_metadata('openpyxl')
datas += copy_metadata('pyclipper')

# ==================== 3. 二进制动态库 ====================
binaries = []

# 收集关键库的动态链接文件
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

# ==================== 4. 排除项（减小体积） ====================
excludes = [
    'tkinter', 'test', 'unittest', 'pytest', 'setuptools', 'pip',
    'IPython', 'jupyter', 'notebook', 'matplotlib.tests',
    'numpy.random._examples', 'pandas.tests',
    'torch.cuda', 'torch.distributed',  # 不需要 GPU 相关模块
]

# ==================== 5. Analysis（主分析） ====================
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

# ==================== 6. EXE（可执行文件） ====================
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='main',                     # 内部可执行文件名，英文避免路径问题
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x86_64',            # 指定 x86_64 架构
    codesign_identity=None,
    entitlements_file=None,
)

# ==================== 7. COLLECT（收集所有文件） ====================
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

# ==================== 8. BUNDLE（生成 .app） ====================
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
