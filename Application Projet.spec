# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# Project path so PyInstaller can find main.py and project modules
project_path = r'C:\Users\thoma\PP\Projet_Coloriage'
pathex = [project_path]

# Locate Tcl/Tk runtime directories in the active environment (conda/miniforge)
possible_tcl = [
    os.path.join(sys.prefix, 'Library', 'tcl'),
    os.path.join(sys.prefix, 'tcl'),
]
tcl_dir = None
for p in possible_tcl:
    if os.path.isdir(p):
        tcl_dir = p
        break

# Base datas (keep your resource files)
datas = [(r'ressources/path.json', 'ressources')]
if tcl_dir:
    datas.append((tcl_dir, 'tcl'))

a = Analysis(
    ['main.py'],
    pathex=pathex,
    binaries=[
        (r'C:\Users\thoma\miniforge3\Library\bin\tcl86t.dll','.'),
        (r'C:\Users\thoma\miniforge3\Library\bin\tk86t.dll','.'),
        (r'C:\Users\thoma\miniforge3\Library\bin\ffi-8.dll','.'),
        (r'C:\Users\thoma\miniforge3\Library\bin\libbz2.dll','.'),
        (r'C:\Users\thoma\miniforge3\Library\bin\sqlite3.dll','.'),
        (r'C:\Users\thoma\miniforge3\pkgs\tbb-2021.13.0-h62715c5_1\Library\bin\tbb12.dll','.')
        ],
    datas=datas,
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='Application Projet',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)