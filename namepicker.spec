# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

added_files = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('students.json', '.'),
    ('main.py', '.'),
    ('使用说明.md', '.'),
]

# 如果app_log.txt存在，则添加它
if os.path.exists('app_log.txt'):
    added_files.append(('app_log.txt', '.'))

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'flask', 
        'werkzeug', 
        'jinja2', 
        'json', 
        'random', 
        'logging', 
        'webbrowser', 
        'socket',
        'threading',
        'werkzeug.exceptions',
        'werkzeug.routing',
        'werkzeug.utils',
        'flask.json',
        'flask.helpers',
        'flask.sessions',
        'flask.templating',
        'flask.logging',
        'flask.ctx',
        'flask.globals',
        'encodings',
        'encodings.utf_8',
        'encodings.gbk',
        'encodings.ascii',
        'time',
        'shutil'
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
    [],
    exclude_binaries=True,
    name='班级点名器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ClassRollCall',
) 