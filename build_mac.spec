# -*- mode: python ; coding: utf-8 -*-

import sys
import os
import glob
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

# 增加递归限制
sys.setrecursionlimit(10000)

# ==================== 路径配置 ====================
venv_path = sys.prefix
site_packages = os.path.join(venv_path, 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages')
user_home = os.path.expanduser('~')
paddleocr_model_path = os.path.join(user_home, '.paddleocr')
easyocr_model_path = os.path.join(user_home, '.EasyOCR')

# ==================== 1. 需要完整打包的包列表 ====================
packages_to_include = [
    'paddleocr', 'paddle', 'paddlepaddle', 'paddlex', 'easyocr', 'cv2', 'opencv_contrib_python', 
    'opencv_python', 'PIL', 'pillow', 'matplotlib', 'scipy', 'numpy', 'scikit_image', 'skimage', 
    'imgaug', 'imageio', 'tifffile', 'lazy_loader', 'fitz', 'PyMuPDF', 'pdfplumber', 'pypdfium2', 
    'pdf2docx', 'pdfminer_six', 'lxml', 'cssselect', 'premailer', 'cssutils', 'requests', 'urllib3', 
    'idna', 'chardet', 'certifi', 'yaml', 'PyYAML', 'ujson', 'protobuf', 'pycryptodome', 'cryptography', 
    'pydantic', 'pydantic_core', 'annotated_types', 'typing_extensions', 'lmdb', 'pyclipper', 'shapely', 
    'pandas', 'openpyxl', 'et_xmlfile', 'fastapi', 'starlette', 'uvicorn', 'click', 'tqdm', 'fire', 
    'visualdl', 'psutil', 'torch', 'torchaudio', 'torchvision', 'networkx', 'huggingface_hub', 'filelock', 
    'fsspec', 'safetensors', 'Cython', 'openpyxl',
]
packages_to_include = list(set(packages_to_include))

# ==================== 2. 收集数据 (Data & Binaries) ====================
manual_datas = []
binaries_list = []

# 收集指定包的数据文件和二进制文件
for pkg in packages_to_include:
    # 尝试标准包路径
    pkg_path = os.path.join(site_packages, pkg)
    if os.path.exists(pkg_path) and os.path.isdir(pkg_path):
        manual_datas.append((pkg_path, pkg))
    else:
        # 尝试 '-' 连接的包路径 (如 package-name)
        alt_pkg = pkg.replace('_', '-')
        alt_path = os.path.join(site_packages, alt_pkg)
        if os.path.exists(alt_path) and os.path.isdir(alt_path):
            manual_datas.append((alt_path, alt_pkg))
    
    # 收集 dist-info 目录
    dist_info_pattern = os.path.join(site_packages, f"{pkg.replace('_', '-')}*.dist-info")
    for di in glob.glob(dist_info_pattern):
        if os.path.isdir(di):
            manual_datas.append((di, os.path.basename(di)))

# 收集动态库 (排除 Tkinter/Qt)
for lib in ['paddle', 'cv2', 'fitz', 'torch', 'torchvision', 'PIL']:
    try:
        libs = collect_dynamic_libs(lib)
        filtered = [(src, dst) for src, dst in libs if not any(x in src for x in ['tkinter', 'Qt'])]
        binaries_list.extend(filtered)
    except Exception as e:
        print(f"Warning: Failed to collect dynamic libs for {lib}: {e}")

# 收集 Cython 数据
manual_datas.extend(collect_data_files('Cython'))

# 尝试收集模型文件 (如果存在)
if os.path.exists(paddleocr_model_path):
    manual_datas.append((paddleocr_model_path, '.paddleocr'))
if os.path.exists(easyocr_model_path):
    manual_datas.append((easyocr_model_path, '.EasyOCR'))

# ==================== 3. 隐藏导入 (Hidden Imports) ====================
hidden_imports = [
    'paddleocr', 'paddle', 'paddlepaddle', 'paddlex', 'easyocr', 'paddleocr.ppocr', 
    'paddleocr.ppocr.data', 'paddleocr.ppocr.postprocess', 'paddleocr.ppocr.utils', 
    'paddleocr.tools', 'paddleocr.tools.infer', 'extract_textpoint_slow', 'extract_textpoint_fast', 
    'extract_batchsize', 'easyocr.easyocr', 'easyocr.detection', 'easyocr.recognition', 
    'imgaug', 'imageio', 'skimage', 'matplotlib', 'PIL', 'scipy', 'networkx', 'packaging', 
    'pyclipper', 'lmdb', 'tqdm', 'shapely', 'fastapi', 'starlette', 'uvicorn', 'pydantic', 'Cython',
]

# 收集子模块
for pkg in ['paddleocr', 'paddle', 'easyocr', 'ppocr', 'imgaug', 'imageio', 'skimage', 'PIL']:
    try:
        hidden_imports.extend(collect_submodules(pkg))
    except Exception as e:
        print(f"Warning: Failed to collect submodules for {pkg}: {e}")

hidden_imports = list(set(hidden_imports))

# ==================== 4. 分析 (Analysis) ====================
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries_list,
    datas=manual_datas,
    hiddenimports=hidden_imports,
    hookspath=['.'],
    runtime_hooks=['fix_imports.py'], # 确保 fix_imports.py 在项目根目录
    excludes=['tkinter', 'PyQt5', 'wx'],
    noarchive=False,
)

pyz = PYZ(a.pure)

# ==================== 5. 生成可执行文件 (EXE) ====================
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='商委订单审核助手服务端', # 输出的可执行文件名
    debug=False,
    strip=False,
    upx=True,
    console=True, # 保持 True 以便调试，或者根据需要改为 False
    target_arch='x86_64', # 强制目标架构
    codesign_identity=None,
    entitlements_file=None,
)

# ==================== 6. 收集文件 (COLLECT) ====================
# 关键修改：直接生成名为 '商委订单审核助手服务端' 的文件夹
# 这样 dist/商委订单审核助手服务端/商委订单审核助手服务端 就是一个有效的路径
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='商委订单审核助手服务端', # 这里必须和 EXE 的 name 一致，生成标准的 one-folder 结构
)
