import sys
from cx_Freeze import setup,Executable
from distutils.core import setup
import py2exe

# Dependencies are automatically detected, but it might need fine tuning.
# build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
# base = None
# if sys.platform == "win32":
#     base = "Win32GUI"


setup(name="convert to hillstone",
      version="1.0",
      # options={"build_exe":build_exe_options},
      # executables=[Executable("trans.py", base=base)],
      author='jlyang',
      author_email='jlyang@hillstonenet.com',
      script_name=['mainframe.py','convert_asa.py',
'convert_excel.py',
'convert_junos.py',
'convert_topsec.py',
'creatdb.py',
'en_mouth_to_num.py',
'mainframe.py',
'opensrcfile.py'],
      )