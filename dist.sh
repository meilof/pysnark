#!/bin/sh

rm -rf PySNARK.egg-info/
python3 setup.py sdist
rm -rf PySNARK.egg-info/
python3 setup.py sdist --formats=zip

