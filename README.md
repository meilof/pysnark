# PySNARK

Recent news:

*13.06.2021*: updated setup instructions for zkinterface (bulletproofs, bellman)

*17.05.2021*: want to use if branches, while and for loops in PySNARK programs? Check out [oblif](https://github.com/meilof/oblif)!

*28.03.2021*: updated to latest zkinterface, now works with bellman and bulletproofs

*03.11.2020*: updated to latest snarkjs

*(This is a re-write of the original version of PySNARK, still available [here](https://github.com/Charterhouse/pysnark).)*

PySNARK lets you program zk-SNARKs (aka verifiable computations) directly in Python 3. For example, the following code runs a SNARK program to compute a cube of a number, generates key material, generates a proof, and verifies it:

```
import sys

from pysnark.runtime import snark

@snark
def cube(x):
    return x*x*x

print("The cube of", sys.argv[1], "is", cube(int(sys.argv[1])))
```

For any computations performed using the PubVal datatype provided by pysnark (or using the `@snark` decorator), the library keeps track of the Rank-1 constraint system of the computation. When the computation finishes,  key material for the computation is generated (or re-used) and a SNARK proof is generated.

Features:

* Pure Python 3.* (libsnark and qaptools backends supported on Windows/Linux/Mac OS)
* Can be used in combination with:
  * [libsnark](https://github.com/scipr-lab/libsnark) (natively or via zkinterface, Pinocchio-style or Groth16 proofs)
  * snarkjs, as a drop-in replacement for circom
  * bulletproofs, bellman (via [zkinterface](https://github.com/QED-it/zkinterface))
  * [qaptools](https://github.com/Charterhouse/qaptools)
* Automatically produce Solidity smart contracts
* Automatically produce snarkjs circuit+witness or verification key+proof+public values
* Support for [integer arithmetic](https://github.com/meilof/pysnark/blob/master/pysnark/runtime.py#L179), [linear algebra](https://github.com/meilof/pysnark/blob/master/pysnark/linalg.py#L3), [arrays with conditional indexing](https://github.com/meilof/pysnark/blob/master/pysnark/array.py#L36), and [hashing](https://github.com/meilof/pysnark/blob/master/pysnark/hash.py#L61)
* For branching, use [oblif](https://github.com/meilof/oblif) or the built-in functions to emulate [if statements](https://github.com/meilof/pysnark/blob/master/pysnark/branching.py#L10) and [if/while/for conditionals](https://github.com/meilof/pysnark/blob/master/pysnark/branching.py#L132)
* See provided [examples](https://github.com/meilof/pysnark/tree/master/examples)

PySNARK may be used for non-commercial, experimental and research purposes; see `LICENSE.md` for details. 
PySNARK is experimental and **not fit for production environment**.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/meilof/pysnark/nobackend?filepath=notebooks%2Ftest.ipynb)

## Installation

```
pip3 install git+https://github.com/meilof/pysnark
```

To use the `libsnark` backend, do

```
pip3 install python-libsnark
```

To use the `qaptools` backend, download and install [qaptools](https://github.com/Charterhouse/qaptools). If qaptoosl are not in the system path, set the `QAPTOOLS_BIN` environment variable to their location. On Windows, the qaptools executables can be placed in the current working directory.

To use the `snarkjs` backend, do:

```
npm install snarkjs
```

## Using PySNARK (libsnark backend)

To try out PySNARK, do the following:

```
cd examples
python cube.py 3
```

If the libsnark backend is available, it will be imported and used by default.
This will execute a SNARK computation to compute the cube of the input value, `3`.
As the comptation prorgresses, a constraint system of the computation is kept.

By default, if available, the libsnark backend will be used. In this case, the following files will be generated:

* `pysnark_ek`: key material to generate proofs for this computation (if the same computation is performed later, this file will be re-used; if another computation is performed, it is rebuilt)
* `pysnark_vk`: key material to verify proofs for this computation
* `pysnark_log`: computation log that can be verified with the `pysnark_vk` key: number of inputs/outputs, followed by the inputs/outputs themselves, followed by a proof that the input/outputs were correctly computed 

PySNARK with libsnark can use the more recent Groth16 proof system instead of traditional Pinocchio proofs by using the libsnarkgg backend:

```
cd examples
rm pysnark_*
PYSNARK_BACKEND=libsnarkgg python3 cube.py 3
```

### Combining with snarkjs

PySNARK with the libsnarkgg backend can automatically produce snarkjs `public.json`, `proof.json` and `verification_key.json` files for the performed verifiable computation:

```
meilofs-air:examples meilof$ PYSNARK_BACKEND=libsnarkgg python3 cube.py 33
The cube of 33 is 35937
*** Trying to read pysnark_ek
*** PySNARK: generating proof pysnark_log (sat=True, #io=2, #witness=2, #constraint=3)
*** Public inputs: 33 35937
*** Verification status: True
meilofs-air:examples meilof$ python3 -m pysnark.libsnark.tosnarkjsgg
meilofs-air:examples meilof$ snarkjs groth16 verify verification_key.json public.json proof.json
[INFO]  snarkJS: OK!
```

## Using PySNARK (snarkjs backend)

PySNARK can be used in combination with snarkjs as a drop-in replacement of programming circuits using circom. PySNARK generates the `circuit.r1cs` file corresponding to the computation constraints and the `witness.wtns` file containing the values for the current computation:

```
$ PYSNARK_BACKEND=snarkjs python3 cube.py 33
The cube of 33 is 35937
snarkjs witness.wtns and circuit.r1cs written; see readme
$ snarkjs powersoftau new bn128 12 pot.ptau -v
...
$ snarkjs powersoftau prepare phase2 pot.ptau pott.ptau -v
...
$ snarkjs zkey new circuit.r1cs pott.ptau circuit.zkey
...
$ snarkjs zkey export verificationkey circuit.zkey verification_key.json
$ snarkjs groth16 prove circuit.zkey witness.wtns proof.json public.json
$ snarkjs groth16 verify verification_key.json public.json proof.json
[INFO]  snarkJS: OK!
$ snarkjs zkey export solidityverifier circuit.zkey verifier.sol
$ snarkjs zkey export soliditycalldata public.json proof.json
```

## Using PySNARK (zkinterface backend: bellman, bulletproofs)

PySNARK with the `zkinterface` backend automatically produces zkinterface files for the computation. These files can be used for example with the bellman and bulletproofs backends of `zkinterface`, see [here](https://github.com/QED-it/zkinterface/tree/master/ecosystem).

Specifically, a `circuit.zkif` file is generated that contains the circuit and constraints and can be used for key generation and verification. A `computation.zkif` file is generated that contains the circuit, constraints, and witness, and can be used by the prover.

To generate a zkif file that should work with the zkinterface libsnark backend (not tested):

```
examples meilof$ PYSNARK_BACKEND=zkinterface python3 cube.py 33
The cube of 33 is 35937
*** zkinterface: writing circuit
*** zkinterface: writing witness
*** zkinterface: writing constraints
*** zkinterface circuit, witness, constraints written to 'computation.zkif'
*** zkinterface: writing circuit
*** zkinterface: writing constraints
*** zkinterface circuit, constraints written to 'circuit.zkif'
``` 

To generate a zkif file for the zkinterface bellman backend and use it:

```
examples meilof$ PYSNARK_BACKEND=zkifbellman python3 cube.py 44
The cube of 44 is 85184
*** zkinterface: writing circuit
*** zkinterface: writing witness
*** zkinterface: writing constraints
*** zkinterface circuit, witness, constraints written to 'computation.zkif'
*** zkinterface: writing circuit
*** zkinterface: writing constraints
*** zkinterface circuit, constraints written to 'circuit.zkif'
examples meilof$ cat circuit.zkif | zkif_bellman setup
Written parameters into /Users/meilof/Subversion/pysnark/examples/bellman-pk
examples meilof$ cat computation.zkif | zkif_bellman prove
Reading parameters from /Users/meilof/Subversion/pysnark/examples/bellman-pk
Written proof into /Users/meilof/Subversion/pysnark/examples/bellman-proof
examples meilof$ cat circuit.zkif | zkif_bellman verify
Reading parameters from /Users/meilof/Subversion/pysnark/examples/bellman-pk
Reading proof from /Users/meilof/Subversion/pysnark/examples/bellman-proof
The proof is valid.
examples meilof$ PYSNARK_BACKEND=zkifbellman python3 cube.py 55
The cube of 55 is 166375
*** zkinterface: writing circuit
*** zkinterface: writing witness
*** zkinterface: writing constraints
*** zkinterface circuit, witness, constraints written to 'computation.zkif'
*** zkinterface: writing circuit
*** zkinterface: writing constraints
*** zkinterface circuit, constraints written to 'circuit.zkif'
examples meilof$ cat computation.zkif | zkif_bellman prove
Reading parameters from /Users/meilof/Subversion/pysnark/examples/bellman-pk
Written proof into /Users/meilof/Subversion/pysnark/examples/bellman-proof
examples meilof$ cat circuit.zkif | zkif_bellman verify
Reading parameters from /Users/meilof/Subversion/pysnark/examples/bellman-pk
Reading proof from /Users/meilof/Subversion/pysnark/examples/bellman-proof
The proof is valid.
```

Here, `bellman-pk` and `circuit.zkif` should be generated by a trusted third party. Provers should get `bellman-pk` and will generate the `zkif` files themselves; verifiers should get `bellan-pk` and `circuit.zkif`.

To generate a zkif file for the zkinterface bulletproofs backend and use it:

```
examples meilof$ PYSNARK_BACKEND=zkifbulletproofs python3 cube.py 33
The cube of 33 is 35937
*** zkinterface: writing circuit
*** zkinterface: writing witness
*** zkinterface: writing constraints
*** zkinterface circuit, witness, constraints written to 'computation.zkif'
*** zkinterface: writing circuit
*** zkinterface: writing constraints
*** zkinterface circuit, constraints written to 'circuit.zkif'
examples meilof$ cat computation.zkif | zkif_bulletproofs prove
Saved proof into bulletproofs-proof
examples meilof$ cat circuit.zkif | zkif_bulletproofs verify
Verifying proof in bulletproofs-proof
```

No trusted setup is needed. The proof `bulletproofs.proof` and the computation description `circuit.zkif` should be distributed to the verifier.

## Using PySNARK (qaptools backend)

We discuss the usage of the PySNARK toolchain based on running one of the provided examples acting as each
of the different types of parties in a verifiable computation: trusted party, prover, or verifier.

### As trusted party

To try out running PySNARK as trusted party performing key generation, do the following:

```
cd examples
python cube.py 3
```

If PySNARK has been correctly installed, this will perform a verifiable computation that will compute the cube of the input value, `3`.
At the same time, it will generate all key material needed to verifiably perform the computation in the script.
(Performing an example computation is the only way to generate this key material.)
PySNARK produces the following files:

* Files that should be kept secret by the trusted party generating the key material:
    * `pysnark_mastersk`: zk-SNARK master secret key
* Files that the trusted party should distribute to provers along with the Python script (i.e., `cube.py` in this case):
    * `pysnark_schedule`: schedule of functions called in the computation
    * `pysnark_masterek`: master evaluation key
    * `pysnark_ek_main`: zk-SNARK evaluation
     key for the main function of the computation
    * `pysnark_eqs_main`: equations for the main function of the computation
    * `pysnark_masterpk`: master public key
* Files that the trusted party should distribute to verifiers:
    * `pysnark_schedule`: schedule of functions called in the computation
    * `pysnark_masterpk`: master public key
    * `pysnark_vk_main`: verificaiton key for the main function
* Files that the prover should distribute to verifiers:
    * `pysnark_proof`: proof that the particular computation was performed correctly
    * `pysnark_values`: input/output values of the computation
* Files that are not needed anymore after the execution:
    * `pysnark_eqs`: equations for the zk-SNARK
    * `pysnark_wires`: wire values of the computation
    
### As prover

To try out running PySNARK as a prover, put the files discussed above (i.e.,  `pysnark_schedule`, `pysnark_masterek`, `pysnark_ek_main`, and `pysnark_eqs_main`) together with `cube.py` in a directory and run the same command:

```
cd examples
python cube.py 3
```

This will perform a verifiable computation based on the previously generated key material.

### As verifier

To try out running PySNARK as a verifier, put the files discussed above (i.e.,  `pysnark_schedule`, `pysnark_masterpk` and `pysnark_vk_main` received from the trusted party, and `pysnark_proof` and `pysnark_values` received from the prover) in a folder and run

```
python -m pysnark.qaptools.runqapver
```

This will verify the computation proof with respect to the input/output values from the `pysnark_values` file, e.g,:

```
# PySNARK i/o
main/o_in: 21
main/o_out: 9261
```

In this case, we have verifiably computed the fact that the cube of 21 is 9261. See the `examples` folder for additional examples.


### Using commitments

PySNARK allows proofs to refer to committed data using [Geppetri](https://eprint.iacr.org/2017/013).
This has three applications:
 - it allows proofs to refer to external private inputs from parties other than the trusted third party;
 - it allows different verifiable computations to share secret data with each other; and
 - it allows to divide a verifiable computation into multiple subcomputations, each with their own evaluation and verification keys (but all based on the same master secret key)

All computations sharing committe data should use the same master secret key.
 
See `examples/testcomm.py` for examples.
 
#### External secret inputs
 
To commit to data, use `pysnark.qaptools.runqapinput`, e.g., to commit to values 1, 2, and 3 using a commitment named `test`, use:

```python -m pysnark.qaptools.runqapinput test 1 2 3```

Alternatively, use `pysnark.qaptools.runqapinput.gencomm` from a Python script.
Share `pysnark_wires_test` with any prover who wants to perform a computation with respect to this committed data, and `pysnark_comm_test` to any verifier. 

Import this data into the verifiable computation with 

```[one,two,three] = pysnark.qaptools.backend.importcomm("test")```

#### Sharing data between verifiable computations

In the first computation, do

```pysnark.qaptools.backend.exportcomm([Var(1),Var(2),Var(3)], "test")```

and share `pysnark_wires_test` and `pysnark_comm_test` with the other prover and the verifier, respectively.

In the second verifiable computation, do

```[one,two,three] = pysnark.qaptools.backend.importcomm("test")```

#### Sharing data between different parts of a verifiable computation

This is implicitly used whenever a function is called that is decorated with `@pysnark.qaptools.backend.subqap`.
When a particular functon is used multiple times in a verifiable computation, using `@pysnark.qaptools.backend.subqap` prevents the circuit for the function to be replicated, resulting in smaller key material (but slower verification). 

## Using PySNARK for smart contracts 

The `qaptools` backand of PySNARK supports the automatic generation of Solidity smart contracts that verify the correctness of the given zk-SNARK.

(Smart contracts can also be implemented using snarkjs with the snarkjs backend, see above.)

First, run a verifiable computation using the `qaptools` backend:

```
PYSNARK_BACKEND=qaptools python3 cube.py 33
```

(on Windows, simply run `python3 cube.py 33` since `qaptools` is the only available backend).

Next, use the following command to generate smart contracts:

```
python -m pysnark.qaptools.contract
```

This generates smart contract `contracts/Pysnark.sol` to verify the previously performed verifiable computation (using library `contracts/Pairing.sol` that is also copied into the directory), and test script `test/TestPysnark.sol` that gives a test case for the contract based on the previous I/O and proof.

To test out the contracts using Truffle, first run `truffle init` from where you are running the above command. 
This functionality is based on ideas from [ZoKrates](https://github.com/JacobEberhardt/ZoKrates). Then run `truffle test` to run the test script and check that the given proof can indeed be verified in Solidity.

Note that `test/TestPysnark.sol` indeed contains the I/O from the computation:
```
pragma solidity ^0.5.0;

import "truffle/Assert.sol";
import "../contracts/Pysnark.sol";

contract TestPysnark {
    function testVerifies() public {
        Pysnark ps = new Pysnark();
        uint[] memory proof = new uint[](22);
        uint[] memory io = new uint[](2);
        proof[0] = ...;
        ...
        proof[21] = ...;
        io[0] = 21; // main/o_in
        io[1] = 9261; // main/o_out
        Assert.equal(ps.verify(proof, io), true, "Proof should verify");
    }
}
```

Smart contracts can also refer to commitments, e.g., as imported with the `pysnark.runtime.importcomm` API call. 
In this case, the commitment becomes an argument to the verification function (a six-valued integer array), and the test case shows how the commitment used in the present computation should be used as value for that argument, e.g.:

```
pragma solidity ^0.5.0;

import "truffle/Assert.sol";
import "../contracts/Pysnark.sol";

contract TestPysnark {
    function testVerifies() public {
        Pysnark ps = new Pysnark(); 
        uint[] memory pysnark_comm_test = new uint[](6);
        pysnark_comm_test[0] = ...;
        ...
        Assert.equal(ps.verify(proof, io, pysnark_comm_test), true, "Proof should verify");
    }
}
```

To get more detailed information about the gas usage of the smart contract, run with Ganache: start ``ganache-cli``; edit ``truffle.js`` to add a development network, e.g.:

```
module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",
      port: 8545,
      network_id: "*" // Match any network id
    }
  }
};
```
and finally, run ``truffle test --network development``.

## Acknowledgements

This software contains contributions by Koninklijke Philips N.V.. Part of this work on this software was carried out as part of the [SODA](https://www.soda-project.eu/) project that has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No 731583.

This software contains contributions by Glenn Xavier. This work was supported by DARPA under Agreement No. HR00112020021.

This software also contains contributions by Meilof Veeningen.

See the [license](https://github.com/meilof/pysnark/blob/master/LICENSE.md) for more information.

