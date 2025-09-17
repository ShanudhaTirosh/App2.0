# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['test2.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include customtkinter assets
        ('venv/Lib/site-packages/customtkinter', 'customtkinter/'),
        # Include yt-dlp data files if any
        ('venv/Lib/site-packages/yt_dlp', 'yt_dlp/'),
    ],
    hiddenimports=[
        'customtkinter',
        'yt_dlp',
        'requests',
        'PIL',
        'tkinter',
        'threading',
        'json',
        'os',
        'urllib.parse',
        'pathlib',
        'queue',
        'subprocess',
        'platform',
        'time',
        're',
        # yt-dlp extractors
        'yt_dlp.extractor',
        'yt_dlp.extractor.youtube',
        'yt_dlp.extractor.instagram',
        'yt_dlp.extractor.tiktok',
        'yt_dlp.extractor.twitter',
        'yt_dlp.extractor.facebook',
        # Additional imports that might be missed
        'yt_dlp.utils',
        'yt_dlp.downloader',
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SocialMediaDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # Add your icon file here
    version='version_info.txt'  # Add version info
)