# -*- mode: python -*-
import os
# from https://stackoverflow.com/a/42419584
import sys
sys.setrecursionlimit(5000)

ROOT = os.path.abspath('.')
block_cipher = None

# main part
a = Analysis(['main.py'],
             pathex=[ROOT],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='qsurveytools',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='bin')

# launcher part
b = Analysis(['launcher.py'],
             pathex=[ROOT],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(b.pure, b.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          b.scripts,
          b.binaries,
          b.zipfiles,
          b.datas,
          [],
          name='qsurveytools',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
