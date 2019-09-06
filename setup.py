#!/usr/bin/env python

# based on https://martinopilia.com/posts/2018/09/15/building-python-extension.html
# and https://github.com/m-pilia/disptools/blob/master/python_c_extension/CMakeLists.txt

import os
import subprocess
import sys

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

# Command line flags forwarded to CMake
cmake_cmd_args = []
for f in sys.argv:
    if f.startswith('-D'):
        cmake_cmd_args.append(f)

for f in cmake_cmd_args:
    sys.argv.remove(f)

class CMakeExtension(Extension):
    def __init__(self, name, cmake_lists_dir='.', **kwa):
        Extension.__init__(self, name, sources=[], **kwa)
        self.cmake_lists_dir = os.path.abspath(cmake_lists_dir)

class CMakeBuild(build_ext):
    def build_extensions(self):
        # Ensure that CMake is present and working
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError('Cannot find CMake executable')

        for ext in self.extensions:
            extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))

            cmake_args = [
                '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={}'.format(extdir),
                '-DCMAKE_SWIG_OUTDIR={}'.format(extdir),
                '-DSWIG_OUTFILE_DIR={}'.format(self.build_temp),
                '-DCMAKE_ARCHIVE_OUTPUT_DIRECTORY={}'.format(self.build_temp),
                '-DPYTHON_EXECUTABLE={}'.format(sys.executable)                
            ]

            cmake_args += cmake_cmd_args

            if not os.path.exists(self.build_temp):
                os.makedirs(self.build_temp)

            # Config
            subprocess.check_call(['cmake', ext.cmake_lists_dir] + cmake_args,
                                  cwd=self.build_temp)

            # Build
            subprocess.check_call(['cmake', '--build', '.'],
                                  cwd=self.build_temp)

setup(name='PySNARK',
      version='0.2',
      description='Python zk-SNARK execution environment',
      author='Meilof Veeningen',
      author_email='meilof@gmail.com',
      url='https://github.com/meilof/pysnark',
      packages=['pysnark'],
      ext_modules=[CMakeExtension("pysnark.libsnark", cmake_lists_dir="depends/python-libsnark")],
      cmdclass={'build_ext': CMakeBuild})

