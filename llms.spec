# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = []
datas += collect_data_files('gradio_client')
datas += collect_data_files('gradio')
datas += collect_data_files('safehttpx')
datas += collect_data_files('groovy')
datas += collect_data_files('dotenv')
datas.append(('src/app.json', '.'))
datas.append(('src/.env', '.'))

a = Analysis(
    ['src/llms.py'],
    pathex=['src'],
    binaries=[],
    datas=datas,
    hiddenimports=['dotenv', 'python-dotenv'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
    module_collection_mode={
        'gradio': 'py'
    },
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='llms',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    onefile=True,
    target_arch=None,
    codesign_identity='bahbpawkah',
    entitlements_file='entitlements.xml',
)
