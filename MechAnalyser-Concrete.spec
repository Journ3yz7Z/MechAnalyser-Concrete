# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['scipy.stats', 'matplotlib.backends.backend_agg']
hiddenimports += collect_submodules('mech_analyser.experiment')


a = Analysis(
    ['run_mechanalyser.py'],
    pathex=[],
    binaries=[],
    datas=[('mech_analyser/ui/icons', 'mech_analyser/ui/icons'), ('LICENSE', '.'), ('SOURCE_NOTICE.md', '.')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MechAnalyser-Concrete',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['mech_analyser\\ui\\icons\\MechAnalyser.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MechAnalyser-Concrete',
)
