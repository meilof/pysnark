import pytest
import pysnark
from pysnark.runtime import PrivVal
from pysnark.fixedpoint import PrivValFxp
from pysnark.boolean import PrivValBool
from pysnark.poseidon_constants import poseidon_constants

@pytest.mark.skipif(pysnark.runtime.backend_name not in poseidon_constants, reason="Unsupported backend")
class TestPoseidonHash():
    # The poseidon_hash module throws an error if a backend is not supported
    # We import from poseidon_hash inside the method so that we only import when 
    # the current backend is supported, preventing exceptions being raised

    @pytest.mark.skipif(pysnark.runtime.backend_name != "zkinterface", reason="Unsupported backend")
    def test_zkinterface_permutation(self):
        from pysnark.poseidon_hash import permute
        output = permute([PrivVal(0), PrivVal(1), PrivVal(2), PrivVal(3), PrivVal(4)])
        result = [0x299c867db6c1fdd79dcefa40e4510b9837e60ebb1ce0663dbaa525df65250465, \
                  0x1148aaef609aa338b27dafd89bb98862d8bb2b429aceac47d86206154ffe053d, \
                  0x24febb87fed7462e23f6665ff9a0111f4044c38ee1672c1ac6b0637d34f24907, \
                  0x0eb08f6d809668a981c186beaf6110060707059576406b248e5d9cf6e78b3d3e, \
                  0x07748bc6877c9b82c8b98666ee9d0626ec7f5be4205f79ee8528ef1c4a376fc7]
        print(output)
        assert all([x.val() == y for (x,y) in zip(output, result)])

    @pytest.mark.skipif(pysnark.runtime.backend_name != "zkifbellman", reason="Unsupported backend")
    def test_zkifbellman_permutation(self):
        from pysnark.poseidon_hash import permute
        output = permute([PrivVal(0), PrivVal(1), PrivVal(2), PrivVal(3), PrivVal(4)])
        result = [0x2a918b9c9f9bd7bb509331c81e297b5707f6fc7393dcee1b13901a0b22202e18, \
                  0x65ebf8671739eeb11fb217f2d5c5bf4a0c3f210e3f3cd3b08b5db75675d797f7, \
                  0x2cc176fc26bc70737a696a9dfd1b636ce360ee76926d182390cdb7459cf585ce, \
                  0x4dc4e29d283afd2a491fe6aef122b9a968e74eff05341f3cc23fda1781dcb566, \
                  0x03ff622da276830b9451b88b85e6184fd6ae15c8ab3ee25a5667be8592cce3b1]
        assert all([x.val() == y for (x,y) in zip(output, result)])

    @pytest.mark.skipif(pysnark.runtime.backend_name != "zkifbulletproofs", reason="Unsupported backend")
    def test_zkifbulletproofs_permutation(self):
        from pysnark.poseidon_hash import permute
        output = permute([PrivVal(0), PrivVal(1), PrivVal(2), PrivVal(3), PrivVal(4)])
        result = [0x2a918b9c9f9bd7bb509331c81e297b5707f6fc7393dcee1b13901a0b22202e18, \
                  0x65ebf8671739eeb11fb217f2d5c5bf4a0c3f210e3f3cd3b08b5db75675d797f7, \
                  0x2cc176fc26bc70737a696a9dfd1b636ce360ee76926d182390cdb7459cf585ce, \
                  0x4dc4e29d283afd2a491fe6aef122b9a968e74eff05341f3cc23fda1781dcb566, \
                  0x03ff622da276830b9451b88b85e6184fd6ae15c8ab3ee25a5667be8592cce3b1]
        assert all([x.val() == y for (x,y) in zip(output, result)])

    def test_lincombfxp(self):
        from pysnark.poseidon_hash import permute
        output = permute([PrivVal(0), PrivVal(1), PrivVal(2), PrivVal(3), PrivVal(4)])

    def test_lincombbool(self):
        from pysnark.poseidon_hash import poseidon_hash
        poseidon_hash([PrivValBool(0), PrivValBool(1), PrivValBool(0), PrivValBool(1), PrivValBool(0)])

    def test_int(self):
        from pysnark.poseidon_hash import poseidon_hash
        with pytest.raises(RuntimeError):
            output = poseidon_hash([PrivVal(0), PrivVal(1), PrivVal(2), PrivVal(3), 4])