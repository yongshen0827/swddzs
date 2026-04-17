# build_mac.spec
# -*- mode: python ; coding: utf-8 -*-

import sys
import os
import glob
import shutil
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

sys.setrecursionlimit(10000)

# ==================== 路径配置 (macOS 适配) ====================
venv_path = sys.prefix
site_packages = os.path.join(venv_path, 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages')

user_home = os.path.expanduser('~')
paddleocr_model_path = os.path.join(user_home, '.paddleocr')
easyocr_model_path = os.path.join(user_home, '.EasyOCR')

# ==================== 1. 需要完整打包的包列表 ====================
packages_to_include = [
    'paddleocr', 'paddle', 'paddlepaddle', 'paddlex', 'easyocr',
    'cv2', 'opencv_contrib_python', 'opencv_python', 'PIL', 'pillow',
    'matplotlib', 'scipy', 'numpy', 'scikit_image', 'skimage', 'imgaug', 'imageio',
    'tifffile', 'lazy_loader',
    'fitz', 'PyMuPDF', 'pdfplumber', 'pypdfium2', 'pdf2docx', 'pdfminer_six',
    'lxml', 'cssselect', 'premailer', 'cssutils',
    'requests', 'urllib3', 'idna', 'chardet', 'certifi',
    'yaml', 'PyYAML', 'ujson', 'protobuf', 'pycryptodome', 'cryptography',
    'pydantic', 'pydantic_core', 'annotated_types', 'typing_extensions',
    'lmdb', 'pyclipper', 'shapely', 'pandas', 'openpyxl', 'et_xmlfile',
    'fastapi', 'starlette', 'uvicorn', 'click',
    'tqdm', 'fire', 'visualdl', 'psutil',
    'torch', 'torchaudio', 'torchvision', 'networkx',
    'huggingface_hub', 'filelock', 'fsspec', 'safetensors',
    'Cython', 'openpyxl',
]

packages_to_include = list(set(packages_to_include))

# ==================== 2. 收集数据 ====================
manual_datas = []
binaries_list = []

for pkg in packages_to_include:
    pkg_path = os.path.join(site_packages, pkg)
    if os.path.exists(pkg_path) and os.path.isdir(pkg_path):
        manual_datas.append((pkg_path, pkg))
    else:
        alt_pkg = pkg.replace('_', '-')
        alt_path = os.path.join(site_packages, alt_pkg)
        if os.path.exists(alt_path) and os.path.isdir(alt_path):
            manual_datas.append((alt_path, alt_pkg))

    dist_info_pattern = os.path.join(site_packages, pkg.replace('_', '-') + '-*.dist-info')
    for di in glob.glob(dist_info_pattern):
        if os.path.isdir(di):
            manual_datas.append((di, os.path.basename(di)))

# ==================== 3. 动态库 ====================
for lib in ['paddle', 'cv2', 'fitz', 'torch', 'torchvision', 'PIL']:
    try:
        libs = collect_dynamic_libs(lib)
        filtered = [(src, dst) for src, dst in libs if not any(x in src for x in ['tkinter', 'Qt'])]
        binaries_list.extend(filtered)
    except:
        pass

# ==================== 4. Cython 数据 ====================
manual_datas.extend(collect_data_files('Cython'))

# ==================== 5. 模型文件（不强制打包，仅收集若存在） ====================
if os.path.exists(paddleocr_model_path):
    manual_datas.append((paddleocr_model_path, '.paddleocr'))
if os.path.exists(easyocr_model_path):
    manual_datas.append((easyocr_model_path, '.EasyOCR'))

# ==================== 6. 隐藏导入 ====================
hidden_imports = [
    'paddleocr', 'paddle', 'paddlepaddle', 'paddlex', 'easyocr',
    'paddleocr.ppocr', 'paddleocr.ppocr.data', 'paddleocr.ppocr.postprocess',
    'paddleocr.ppocr.utils', 'paddleocr.tools', 'paddleocr.tools.infer',
    'extract_textpoint_slow', 'extract_textpoint_fast', 'extract_batchsize',
    'easyocr.easyocr', 'easyocr.detection', 'easyocr.recognition',
    'imgaug', 'imageio', 'skimage', 'matplotlib', 'PIL',
    'scipy', 'networkx', 'packaging', 'pyclipper', 'lmdb', 'tqdm', 'shapely',
    'fastapi', 'starlette', 'uvicorn', 'pydantic', 'Cython',
]
for pkg in ['paddleocr', 'paddle', 'easyocr', 'ppocr', 'imgaug', 'imageio', 'skimage', 'PIL']:
    try:
        hidden_imports.extend(collect_submodules(pkg))
    except:
        pass
hidden_imports = list(set(hidden_imports))

# ==================== 7. Analysis ====================
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries_list,
    datas=manual_datas,
    hiddenimports=hidden_imports,
    hookspath=['.'],
    runtime_hooks=['fix_imports.py'],
    excludes=['tkinter', 'PyQt5', 'wx'],
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
    entitlements_file=None,
)

# ==================== 关键修改：清理旧冲突，安全命名 COLLECT ====================
# 如果 dist 目录下存在与目标同名的文件，先删除它（防止冲突）
target_collect_dir = os.path.join('dist', 'app_contents_temp')
if os.path.isfile(target_collect_dir):
    os.remove(target_collect_dir)
elif os.path.isdir(target_collect_dir):
    shutil.rmtree(target_collect_dir)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='app_contents_temp',   # 使用临时名称，避免与最终 .app 混淆
)
