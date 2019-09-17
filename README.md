# PySNARK

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

PySNARK can use [qaptools](https://github.com/Charterhouse/qaptools) or [libsnark](https://github.com/scipr-lab/libsnark) as backend. For any computations performed using the PubVal datatype provided by pysnark (or using the `@snark` decorator), the library keeps track of the Rank-1 constraint system of the computation. When the computation finishes,  key material for the computation is generated (or re-used) and a SNARK proof is generated.

The [previous PySNARK](https://github.com/Charterhouse/pysnark) also inclded functionality to automatically turn the zk-SNARK into a Solidity smart contracts for use on the Ethereum blockchain. This functionality is not available in the current version yet.

PySNARK may be used for non-commercial, experimental and research purposes; see `LICENSE.md` for details. 
PySNARK is experimental and **not fit for production environment**.

## Installation

PySNARK requires Python 3.*.

### Requirements for libsnark backend

The libsnark module requires SWIG, a C++ compiler, Python3 header files, CMake, and the GNU MP library. See [here](https://github.com/scipr-lab/libsnark) for details. On Linux, the following has been found to work to satisfy the requirements:

```
sudo apt-get install pkg-config build-essential cmake git libgmp3-dev libprocps-dev python-markdown libboost-all-dev libssl-dev
```

### Requirements for qaptools backend

To compile the qaptools backend, a C++ compiler is needed. For Windows, qaptools binaries can be downloaded [here](https://github.com/Charterhouse/qaptools).

### Building

Download PySNARK including submodules:

```
git clone --recursive https://github.com/meilof/pysnark.git
```

Build and install PySNARK (assuming `python` is Python 3):

```
python setup.py install
```

To disable the qaptools backend, use `--disable-qaptools`. To disable the libsnark backend, use `--disable-libsnark`. To specify locations of precompiled qaptools binaries (e.g., for Windows), use `--qaptools=bin=<dir>`. Any CMake arguments (`-D...`), for example, for libsnark, can be given direcly on the above command line. For example, on Mac OS X I use `python3 setup.py install -DCMAKE_PREFIX_PATH=/usr/local/Cellar/openssl/1.0.2s -DCMAKE_SHARED_LINKER_FLAGS=-L/usr/local/Cellar/openssl/1.0.2s/lib -DWITH_PROCPS=OFF -DWITH_SUPERCOP=OFF -DOPT_FLAGS=-std=c++11`.


## Using PySNARK (libsnark backend)

To try out PySNARK, do the following:

```
cd examples
python cube.py 3
```

This will execute a SNARK computation to compute the cube of the input value, `3`.
As the comptation prorgresses, a constraint system of the computation is kept.

By default, if available, the libsnark backend will be used. In this case, the following files will be generated:

* `pysnark_ek`: key material to generate proofs for this computation (if the same computation is performed later, this file will be re-used; if another computation is performed, it is rebuilt)
* `pysnark_vk`: key material to verify proofs for this computation
* `pysnark_log`: computation log that can be verified with the `pysnark_vk` key: number of inputs/outputs, followed by the inputs/outputs themselves, followed by a proof that the input/outputs were correctly computed 


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

## Acknowledgements

Part of this work on this software was carried out as part of the [SODA](https://www.soda-project.eu/) project that has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No 731583.

