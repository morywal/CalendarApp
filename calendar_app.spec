"""
PyInstaller spec file for the AI Calendar App.
This file configures how PyInstaller packages the application.
"""
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

console=False

# Collect all necessary data files
datas = []
datas += collect_data_files('flask')
datas += collect_data_files('app')

# Add static and template folders explicitly
datas += [
    ('app/static', 'app/static'),
    ('app/templates', 'app/templates'),
]

# Collect all necessary modules
hiddenimports = []
hiddenimports += collect_submodules('flask')
hiddenimports += collect_submodules('flask_login')
hiddenimports += collect_submodules('flask_wtf')
hiddenimports += collect_submodules('flask_sqlalchemy')
hiddenimports += collect_submodules('wtforms')
hiddenimports += collect_submodules('email_validator')
hiddenimports += collect_submodules('sqlalchemy')
hiddenimports += collect_submodules('scikit-learn')
hiddenimports += collect_submodules('numpy')
hiddenimports += collect_submodules('scipy')
hiddenimports += collect_submodules('app')

a = Analysis(
    ['app_entry.py'],
    pathex=[os.path.abspath(os.getcwd())],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure, 
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AI_Calendar_Assistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app/static/img/calendar_icon.ico' if os.path.exists('app/static/img/calendar_icon.ico') else None,
)
