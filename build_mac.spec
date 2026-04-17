# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 手动添加 OCR 模型路径（如果 PyInstaller 没自动包含）
        # ('/Users/runner/.paddleocr', '.paddleocr'),
        # ('/Users/runner/.EasyOCR', '.EasyOCR'),
    ],
    hiddenimports=[
        # 列出 PyInstaller 可能漏掉的核心包
        'paddleocr', 'easyocr', 'cv2', 'PIL', 'numpy', 'scipy', 
        'skimage', 'matplotlib', 'yaml', 'pkg_resources.py2_warn'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 简单的 PYZ
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 核心：强制指定目标架构为 x86_64
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='商委订单审核助手服务端',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    # 关键：指定架构
    target_arch='x86_64', 
    console=True, # 根据你的需求设置 True 或 False
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_name=None,
    codesign_identity=None,
    entitlements_file=None,
)

# 收集所有文件到一个目录
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='商委订单审核助手服务端', # 这个名字必须和 EXE 一致
)
