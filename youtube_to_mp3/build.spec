# -*- mode: python ; coding: utf-8 -*-

import os
import glob

block_cipher = None

# Detectar automáticamente la carpeta de ffmpeg
base_dir = os.path.dirname(os.path.abspath(SPEC))
ffmpeg_folders = glob.glob(os.path.join(base_dir, "ffmpeg", "ffmpeg-*"))
ffmpeg_path = ffmpeg_folders[0] if ffmpeg_folders else None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'yt_dlp',
        'mutagen',
        'PIL',
        'requests',
        'PyQt6',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
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
    name='YouTubeToMP3',
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

# Copiar FFmpeg al directorio de distribución
if ffmpeg_path:
    import shutil
    dest_ffmpeg = os.path.join('dist', 'ffmpeg', os.path.basename(ffmpeg_path))
    if os.path.exists(dest_ffmpeg):
        shutil.rmtree(dest_ffmpeg)
    shutil.copytree(ffmpeg_path, dest_ffmpeg)
    print(f"✅ FFmpeg copiado desde: {ffmpeg_path}")
else:
    print("⚠️  No se encontró FFmpeg.")