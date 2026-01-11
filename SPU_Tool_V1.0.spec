# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for SPU Tool V1.0 - Single EXE

block_cipher = None

a = Analysis(
    ['main_tkinter.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),
        ('src', 'src'),
    ],
    hiddenimports=[
        'pandas',
        'openpyxl',
        'openpyxl.cell._writer',
        'numpy',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        # Source modules
        'src',
        'src.gui',
        'src.excel_handler',
        'src.processor',
        'src.utils',
        'src.mapping_engine',
        'src.validator',
        'src.logger',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'streamlit',
        'matplotlib',
        'scipy',
        'PIL',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SPU_Tool_V1.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI app (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one: icon='icon.ico'
)
