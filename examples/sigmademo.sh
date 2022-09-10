#!/bin/sh

python3 sigmasetup.py 
python3 sigmacommit.py age:33 salary:31000
PYSNARK_BACKEND=sigmaprover python3 sigmademo.py 
PYSNARK_BACKEND=sigmaverifier python3 sigmademo.py 
