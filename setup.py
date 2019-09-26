#!/usr/bin/env python

# based on https://martinopilia.com/posts/2018/09/15/building-python-extension.html
# and https://github.com/m-pilia/disptools/blob/master/python_c_extension/CMakeLists.txt

import os
import os.path
import shutil
import subprocess
import sys

import setuptools.command.egg_info
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

# Command line flags forwarded to CMake
cmake_cmd_args = []
for f in sys.argv:
    if f.startswith('-D'):
        cmake_cmd_args.append(f)
for f in cmake_cmd_args:
    sys.argv.remove(f)
    
disable_libsnark = False
if "--disable-libsnark" in sys.argv:
    disable_libsnark = True
    sys.argv.remove("--disable-libsnark")
if not os.path.isfile("depends/python-libsnark/CMakeLists.txt"):
    print("*** depends/python-libsnark/CMakeLists.txt not found, disabling libsnark backend")
    disable_libsnark = True

disable_qaptools = False
if "--disable-qaptools" in sys.argv:
    disable_qaptools = True
    sys.argv.remove("--disable-qaptools")
    
qaptools_bin = None
for i in sys.argv:
    if i.startswith("--qaptools-bin="):
        qaptools_bin = i[15:]
        sys.argv.remove(i)
        break
        
if qaptools_bin is None and os.path.isfile("qaptools/qapgen" + (".exe" if os.name=="nt" else "")):
    print("*** Using detected qaptools in qaptools/")
    qaptools_bin="qaptools"
    
if qaptools_bin is None and not os.path.isfile("depends/qaptools/CMakeLists.txt"):
    print("*** depends/qaptools/CMakeLists.txt not found, disabling libsnark backend")
    disable_qaptools = True
    
# write manifest
print("writing MANIFEST.in")
mfest = open("MANIFEST.in", "w")
print("recursive-include examples *.py", file=mfest)
print("include examples/binarycircuit_example.txt", file=mfest)
if not disable_qaptools:
    if qaptools_bin:
        print("recursive-include", qaptools_bin, "*", file=mfest)
    else:
        print("recursive-include depends/qaptools *", file=mfest)
if not disable_libsnark: print("recursive-include depends/python-libsnark *", file=mfest)
print("include LICENSE.md", file=mfest)
mfest.close()

        
def use_qaptools_bins(target):
    apps = ['qapgen', 'qapgenf', 'qapinput', 'qapcoeffcache', 'qapprove', 'qapver']
    exefix = '.exe' if os.name == 'nt' else ''

    for app in apps:
         shutil.copy2(qaptools_bin+'/'+app, target+"/"+app)
    
if "-h" in sys.argv or "--help" in sys.argv:
    print("PySNARK setup.py\n\n" +
          "PySNARK options:\n\n" +
    
          "  --disable-libsnark  disable libsnark backend\n" +
          "  --disable-qaptools  disable qaptools backend\n" +
          "  --qaptools=bin=...  use precompiled qaptools from given directory\n" +
          "  -D...               arguments for cmake compilation of libsnark/qaptools\n")

class CMakeExtension(Extension):
    def __init__(self, name, cmake_lists_dir='.', **kwa):
        Extension.__init__(self, name, sources=[], **kwa)
        self.cmake_lists_dir = os.path.abspath(cmake_lists_dir)
        self.prefun = kwa["prefun"] if "prefun" in kwa else None

class CMakeBuild(build_ext):
    def build_extensions(self):
        # Ensure that CMake is present and working
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError('Cannot find CMake executable')

        for ext in self.extensions:
            extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
            tempdir = self.build_temp+"/"+ext.name
            if not os.path.exists(tempdir):
                os.makedirs(tempdir)
            
            if ext.prefun:
                ext.prefun(extdir)
                continue

            cmake_args = [
                '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={}'.format(extdir),
                '-DCMAKE_RUNTIME_OUTPUT_DIRECTORY={}'.format(extdir),
                '-DCMAKE_SWIG_OUTDIR={}'.format(extdir),
                '-DSWIG_OUTFILE_DIR={}'.format(tempdir),
                '-DCMAKE_ARCHIVE_OUTPUT_DIRECTORY={}'.format(tempdir),
                '-DPYTHON_EXECUTABLE={}'.format(sys.executable)                
            ]
            cmake_args += cmake_cmd_args
                
            subprocess.check_call(['cmake', ext.cmake_lists_dir] + cmake_args, cwd=tempdir)
            #subprocess.check_call(['make', 'VERBOSE=1'], cwd=tempdir)
            subprocess.check_call(['cmake', '--build', '.'], cwd=tempdir)

if disable_qaptools and disable_libsnark:  
    my_exts = None
else:
    my_exts=[] + ([CMakeExtension("pysnark.libsnark.all", cmake_lists_dir="depends/python-libsnark")] if not disable_libsnark else []) + ([CMakeExtension("pysnark.qaptools.all", cmake_lists_dir="depends/qaptools", prefun=use_qaptools_bins if not qaptools_bin is None else None) if not disable_qaptools else []])


setup(name='PySNARK',
      version='0.2' + ('-nols' if disable_libsnark else '') + ('-noqt' if disable_qaptools else ''),
      description='Python zk-SNARK execution environment',
      author='Meilof Veeningen',
      author_email='meilof@gmail.com',
      url='https://github.com/meilof/pysnark',
      packages=['pysnark'] +
                  (['pysnark.qaptools'] if not disable_qaptools else []) +
                  (['pysnark.libsnark'] if not disable_libsnark else []),
      package_data={'pysnark.qaptools': []} if not disable_qaptools else {},
      ext_modules = my_exts,
      cmdclass={'build_ext': CMakeBuild} if not (disable_qaptools and disable_libsnark) else {}
)

