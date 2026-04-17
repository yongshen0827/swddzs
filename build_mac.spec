# build_mac.spec
# -*- mode: python ; coding: utf-8 -*-

import sys
import os
import glob
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

sys.setrecursionlimit(10000)

# ==================== 路径配置 (macOS) ====================
venv_path = sys.prefix
site_packages = os.path.join(venv_path, 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages')

user_home = os.path.expanduser('~')
paddleocr_model_path = os.path.join(user_home, '.paddleocr')
easyocr_model_path = os.path.join(user_home, '.EasyOCR')

# ==================== 1. 核心包列表 ====================
packages_to_include = [
    'paddleocr', 'paddle', 'paddlepaddle', 'paddlex', 'easyocr',
    'cv2', 'PIL', 'pillow', 'matplotlib', 'scipy', 'numpy', 'skimage',
    'fitz', 'PyMuPDF', 'pdfplumber', 'pdfminer',
    'requests', 'urllib3', 'certifi',
    'yaml', 'pydantic', 'fastapi', 'uvicorn',
    'torch', 'torchvision', 'torchaudio', 'Cython', 'openpyxl',
]

# ==================== 2. 收集数据和二进制 ====================
datas = []
binaries = []

# 自动收集 paddle 的动态库（关键！）
try:
    paddle_binaries = collect_dynamic_libs('paddle')
    binaries.extend(paddle_binaries)
    print(f"Collected {len(paddle_binaries)} paddle dynamic libs")
except Exception as e:
    print(f"Warning: Could not collect paddle dynamic libs: {e}")

# 自动收集 cv2 的动态库
try:
    binaries.extend(collect_dynamic_libs('cv2'))
except:
    pass

# 自动收集 torch 的动态库
try:
    binaries.extend(collect_dynamic_libs('torch'))
except:
    pass

# 收集数据文件
for pkg in packages_to_include:
    try:
        datas.extend(collect_data_files(pkg))
    except:
        pass

# 模型文件（可选）
if os.path.exists(paddleocr_model_path):
    datas.append((paddleocr_model_path, '.paddleocr'))
if os.path.exists(easyocr_model_path):
    datas.append((easyocr_model_path, '.EasyOCR'))

# ==================== 3. 隐藏导入 ====================
hiddenimports = [
    'paddleocr', 'paddle', 'paddlepaddle', 'paddlex', 'easyocr',
    'cv2', 'PIL', 'fitz', 'pdfplumber', 'openpyxl',
    'skimage', 'matplotlib', 'scipy', 'Cython',
    'pydantic', 'fastapi', 'uvicorn', 'starlette',
]
for pkg in ['paddleocr', 'paddle', 'easyocr', 'skimage']:
    try:
        hiddenimports.extend(collect_submodules(pkg))
    except:
        pass
hiddenimports = list(set(hiddenimports))

# ==================== 4. Analysis ====================
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],  # 不再使用自定义钩子目录
    runtime_hooks=['fix_imports.py'],  # 保留你的运行时修复脚本
    excludes=['tkinter', 'PyQt5', 'wx', 'IPython'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='商委订单审核助手服务端',
    debug=False,
    strip=False,
    upx=True,
    console=True,
    target_arch=None,
    codesign_identity=None,
)

app = BUNDLE(
    exe,
    name='商委订单审核助手服务端.app',
    bundle_identifier='com.ocr.verify',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': True,
        'CFBundleShortVersionString': '1.1.2',
        'CFBundleVersion': '1.1.2',
        'CFBundleExecutable': '商委订单审核助手服务端',
    },
)
