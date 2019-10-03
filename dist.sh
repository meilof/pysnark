#!/bin/sh

rm -rf PySNARK.egg-info/
python3 setup.py sdist
rm -rf PySNARK.egg-info/
python3 setup.py --disable-libsnark --qaptools-bin=qaptools/ sdist --formats=zip