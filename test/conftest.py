import pytest
from pysnark import runtime

@pytest.fixture(scope="session")
def disable_output():
    """
    Disables all circuit outputs when running tests
    """
    yield
    runtime.autoprove = False

def load_backend(backend):
    import sys
    import importlib
    from pysnark import runtime

    backends = [
        ["libsnark",    "pysnark.libsnark.backend"],
        ["libsnarkgg",  "pysnark.libsnark.backendgg"],
        ["qaptools",    "pysnark.qaptools.backend"],
        ["snarkjs",     "pysnark.snarkjsbackend"],
        ["zkinterface", "pysnark.zkinterface.backend"],
        ["zkifbellman", "pysnark.zkinterface.backendbellman"],
        ["zkifbulletproofs", "pysnark.zkinterface.backendbulletproofs"],    
        ["nobackend",   "pysnark.nobackend"]
    ]

    for mod in backends:
        if backend == mod[0]:
            runtime.backend = importlib.import_module(mod[1])
            return

    raise RuntimeError("Invalid backend for test")