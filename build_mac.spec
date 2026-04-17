# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
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

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 1. EXE 的名字：这是实际运行的二进制文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='商委订单审核助手服务端',  # <--- 保持不变，这是程序名
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    target_arch='x86_64', 
    console=True, 
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_name=None,
    codesign_identity=None,
    entitlements_file=None,
)

# 2. COLLECT 的名字：这是输出目录的名字 (修改这里！)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app_contents_temp',  # <--- 修改这里！不要和 EXE name 一样
)
