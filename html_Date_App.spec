# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['html_Date_App.py'],
    pathex=[],
    binaries=[],
    datas=[('/Users/hsuyueht/Library/Python/3.9/lib/python/site-packages/whisper/assets/mel_filters.npz', 'whisper/assets/'), ('/Users/hsuyueht/Library/Python/3.9/lib/python/site-packages/whisper/assets/multilingual.tiktoken', 'whisper/assets/')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='html_Date_App',
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
    icon=['pharm.icns'],
)
app = BUNDLE(
    exe,
    name='html_Date_App.app',
    icon='pharm.icns',
    bundle_identifier=None,
)
