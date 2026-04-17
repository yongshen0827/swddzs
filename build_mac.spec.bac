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
    a.datas,
    [],
    name='商委订单审核助手服务端', # 打包出的二进制文件名
    debug=False,
    strip=False,
    upx=True,
    console=True,
    target_arch='x86_64',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='app_contents_temp', # 打包出的资源文件夹名 (关键!)
)
