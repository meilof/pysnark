# Copyright (c) 2016-2018 Koninklijke Philips N.V. All rights reserved. A
# copyright license for redistribution and use in source and binary forms,
# with or without modification, is hereby granted for non-commercial,
# experimental and research purposes, provided that the following conditions
# are met:
# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimers.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimers in the
#   documentation and/or other materials provided with the distribution. If
#   you wish to use this software commercially, kindly contact
#   info.licensing@philips.com to obtain a commercial license.
#
# This license extends only to copyright and does not include or grant any
# patent license or other license whatsoever.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import random
import subprocess
import sys

from . import options
from . import runqapgen


def run(bname):
    """
    Run the qapinput tool to build a commitment file representing some data.
    The input file (given by :py:fn:`pysnark.options.get_block_file`) consists
    of one value per line, plus a last line of randomness. The output file
    generated is given by :py:fn:`pysnark.options.get_block_comm`.

    :param bname: Block name
    :return: None
    """

    bfile = options.get_block_file(bname)
    bcomm = options.get_block_comm(bname)

    mpkey = options.get_mpkey_file()
    print("*** building block commitment", bcomm, "from wires", bfile, file=sys.stderr)

    blockcomm = open(bcomm, "w")
    outs = None if options.qaptools_debug() else subprocess.DEVNULL
    ret = subprocess.call([options.get_qaptool_exe("qapinput"), mpkey, bfile], stdout=blockcomm, stderr=outs)
    blockcomm.close()
    if ret != 0:
        raise RuntimeError("qapinput failed")


def writecomm(blocknm, vals, rnd=None):
    """
    Write values to a commitment file

    :param bfile: Block name
    :param data: List of integer values to commit to
    :param rnd: Randomness for the commitment (or generate if not given)
    :return: None
    """

    if rnd is None: rnd = random.SystemRandom().randint(0, options.vc_p-1)
    blockfile = open(options.get_block_file(blocknm), "w")
    for val in vals: print(val, file=blockfile)
    print(rnd, file=blockfile)
    blockfile.close()


def gencomm(blocknm, vals, rnd=None):
    """
    Generate commitment file and commitment

    :param blocknm: Block name
    :param vals: List of integer values to commit to
    :param rnd: Randomness for the commitment (or generate if not given)
    :return: None
    """

    writecomm(blocknm, vals, rnd)
    runqapgen.ensure_mkey(-1, len(vals))
    run(blocknm)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("*** Usage:", sys.argv[0], "<bname> [values]", file=sys.stderr)
        sys.exit(2)

    vals = []

    if len(sys.argv) == 2:
        for ln in sys.stdin:
            vals.extend(list(map(int, ln.strip().split())))
    else:
        vals.extend(list(map(int, sys.argv[2:])))

    writecomm(sys.argv[1], vals)
    runqapgen.ensure_mkey(-1, len(vals))
    run(sys.argv[1])