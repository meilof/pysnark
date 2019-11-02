#!/usr/bin/env python

from setuptools import setup

setup(name='PySNARK',
      version='0.3',
      description='Python zk-SNARK execution environment',
      author='Meilof Veeningen',
      author_email='meilof@gmail.com',
      url='https://github.com/meilof/pysnark',
      packages=['pysnark','pysnark.qaptools','pysnark.libsnark', 'pysnark.zkinterface'],
      package_data={'pysnark.qaptools': ['*.sol']},
      extras_require={
        'libsnark':  ["python-libsnark>=0.3.1"],
      },
)
