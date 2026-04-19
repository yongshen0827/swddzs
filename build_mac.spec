# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import platform
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs, copy_metadata

block_cipher = None

# --- 1. 动态库与隐藏导入配置 (适配 PaddleOCR 3.x + PyTorch) ---
hiddenimports = [
    # Paddle 和 PaddleOCR 核心模块 (3.x)
    'paddle', 'paddleocr', 'paddlex',
    'paddle.fluid', 'paddle.base', 'paddle.dataset',
    
    # PaddleOCR 3.x 内部实际模块（由 collect_submodules 自动收集，此处仅作安全兜底）
    'paddleocr._pipelines', 'paddleocr._pipelines.ocr',
    'paddlex.inference', 'paddlex.inference.pipelines',
    
    # PyTorch 相关（修复 torch.cuda 缺失）
    'torch', 'torch.cuda', 'torch.cuda.amp', 'torch.cuda.streams',
    'torch.distributed', 'torch.distributed.rpc',
    'torchvision', 'torchaudio',
    
    # 其他关键依赖
    'easyocr', 'cv2', 'sklearn', 'skimage',
    'scipy._cyutility_cxx',          # scipy 新版本内部模块名
    'scipy.special._ufuncs',
    'scipy.linalg.cython_blas',
    'scipy.linalg.cython_lapack',
    'scipy.sparse._csparsetools',
    'uvicorn', 'fastapi', 'pydantic', 'fitz', 'pdfplumber',
    
    # 处理 setuptools / pkg_resources 的潜在缺失
    'pkg_resources', 'pkg_resources._vendor', 'pkg_resources.extern',
    
    # modelscope 依赖（PaddleX 间接依赖）
    'modelscope', 'modelscope.utils', 'modelscope.utils.logger',
    'modelscope.utils.torch_utils', 'modelscope.utils.import_utils',
    'modelscope.utils.ast_utils', 'modelscope.utils.registry',
]

# 自动收集子模块，防止遗漏（会覆盖上述手动添加）
hiddenimports += collect_submodules('paddleocr')
hiddenimports += collect_submodules('paddle')
hiddenimports += collect_submodules('paddlex')
hiddenimports += collect_submodules('torch')
hiddenimports += collect_submodules('modelscope')
hiddenimports = list(set(hiddenimports))

# 移除不存在的模块（避免警告）
for invalid_mod in ['paddleocr.tools', 'paddleocr.ppocr', 'paddleocr.ppstructure', 
                    'paddle.utils._cpp_infer', 'scipy._cyutility', 'importlib_resources.trees']:
    if invalid_mod in hiddenimports:
        hiddenimports.remove(invalid_mod)

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
datas += collect_data_files('scikit-learn')   # sklearn 的正确包名

# --- 新增：收集必要的元数据（解决 PaddleX 依赖检查失败）---
metadata_datas = []
for pkg in ['paddlex', 'ftfy', 'imagesize', 'lxml', 'opencv-contrib-python', 
            'openpyxl', 'pyclipper', 'modelscope', 'torch', 'torchvision', 'torchaudio']:
    try:
        metadata_datas += copy_metadata(pkg)
    except Exception as e:
        print(f"警告: 无法复制 {pkg} 的元数据: {e}")
datas += metadata_datas

# --- 3. 二进制动态库 (核心: 解决 "Illegal instruction" 及路径问题) ---
binaries = []
# 显式收集 Paddle 和 Torch 的动态库，确保指令集兼容的版本被正确打包
binaries += collect_dynamic_libs('paddle')
binaries += collect_dynamic_libs('torch')
binaries += collect_dynamic_libs('torchvision')
binaries += collect_dynamic_libs('torchaudio')
binaries += collect_dynamic_libs('cv2')
binaries += collect_dynamic_libs('numpy')
binaries += collect_dynamic_libs('scipy')
binaries += collect_dynamic_libs('PIL')
binaries += collect_dynamic_libs('scikit-learn')

# 手动将 Paddle 的 libs 目录打包到 .app/Contents/MacOS/ 下（关键修复）
try:
    import paddle
    paddle_libs_dir = os.path.join(os.path.dirname(paddle.__file__), 'libs')
    if os.path.exists(paddle_libs_dir):
        # 将整个目录打包到可执行文件同级目录下的 paddle/libs
        binaries.append((paddle_libs_dir, 'paddle/libs'))
        print(f"✅ 已收集 Paddle libs 目录: {paddle_libs_dir} -> paddle/libs")
except Exception as e:
    print(f"⚠️ 无法收集 Paddle libs 目录: {e}")

# 同样处理 torch 的 lib 目录（如果存在）
try:
    import torch
    torch_lib_dir = os.path.join(os.path.dirname(torch.__file__), 'lib')
    if os.path.exists(torch_lib_dir):
        binaries.append((torch_lib_dir, 'torch/lib'))
        print(f"✅ 已收集 Torch lib 目录: {torch_lib_dir} -> torch/lib")
except Exception as e:
    print(f"⚠️ 无法收集 Torch lib 目录: {e}")

# --- 4. 排除项 (减小体积，但保留必要的子模块) ---
excludes = [
    'tkinter', 'test', 'unittest', 'pytest', 'setuptools', 'pip',
    'IPython', 'jupyter', 'notebook', 'matplotlib.tests',
    'torch.distributed',          # 分布式训练，无需打包
    'paddle.tensorrt',            # TensorRT 依赖，macOS 无需
    'paddlex.inference.serving',  # serving 插件，无需打包
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
    target_arch=None,            # 避免与命令行参数冲突
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
