import pytest
from pysnark import runtime

@pytest.fixture(scope="session")
def disable_output():
    """
    Disables all circuit outputs when running tests
    """
    yield
    runtime.autoprove = False