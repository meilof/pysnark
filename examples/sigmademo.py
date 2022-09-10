# from __future__ import print_function

import secrets
import sys

import pysnark.runtime

from pysnark.runtime import snark, PrivVal

comms = pysnark.runtime.backend.read_commitments()

pysnark.runtime.bitlength = 7
comms["age"].assert_gt(30)
pysnark.runtime.bitlength = 20
comms["salary"].assert_ge(30000)
