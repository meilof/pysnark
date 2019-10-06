# Copyright (C) Meilof Veeningen, 2019

from .backend import *
import pysnark.libsnark.backend

pysnark.libsnark.backend.use_groth = True