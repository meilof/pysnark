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

import os
import subprocess
import sys

from . import options


def run(eksize, pksize, genmk=False):
    """
    Run the qapgen tool

    :param eksize: Desired master evaluation key size
    :param pksize: Desired master public key size
    :param genmk: True if a new master secret key should be generated, False otherwise
    :return: None
    """
    mskfile = options.get_mskey_file()
    mkeyfile = options.get_mkey_file()
    mpkeyfile = options.get_mpkey_file()

    if not genmk and not os.path.isfile(mskfile):
        raise IOError("Could not enlarge master key materiak: master secret key missing")

    print("*** " + ("generating" if genmk else "enlarging") + " master key material", file=sys.stderr)
    outs = None if options.qaptools_debug() else subprocess.DEVNULL
    if subprocess.call([options.get_qaptool_exe("qapgen"), str(max(pksize,eksize,0)), str(max(pksize,0)),
                        mskfile, mkeyfile, mpkeyfile], stdout=outs, stderr=outs) != 0:
        raise RuntimeError("qapgen failed")


def get_mekey_size():
    """
    Get the size (maximal exponent) of the current master evaluation key

    :return: Size, or -1 if key does not exist
    """
    try:
        mekf = open(options.get_mkey_file())
        curmk = int(next(mekf).strip().split(" ")[2])
        mekf.close()
        return curmk
    except IOError:
        return -1


def get_mpkey_size():
    """
    Get the size (maximal exponent) of the current master public key

    :return: Size, or -1 if key does not exist
    """
    try:
        mpkf = open(options.get_mpkey_file())
        curmpk = int(next(mpkf).strip().split(" ")[2])
        mpkf.close()
        return curmpk
    except IOError:
        return -1


def ensure_mkey(eksize, pksize):
    """
    Ensures that there are master evaluation and public keys of the given sizes.

    If master evaluation/public keys exist but are to small, and there is no
    master secret key, this raises an error.

    If there is no key material at all, a fresh master secret key will be
    generated.

    :param eksize: Minimal evaluation key size (-1 if not needed)
    :param pksize: Minimal public key size (-1 if not needed)
    :return: Actual evaluation key, public key size after key generation
    """

    curek = get_mekey_size()
    curpk = get_mpkey_size()

    havemsk = os.path.isfile(options.get_mskey_file())
    havekeys = os.path.isfile(options.get_mpkey_file()) or os.path.isfile(options.get_mkey_file())

    if curek < eksize or curpk < pksize:
        if havemsk:
            run(max(curek, eksize), max(curpk, pksize), False)
            return (max(curek, eksize), max(curpk, pksize))
        elif havekeys:
            raise IOError("Key material too small ("+str(curek)+","+str(curpk)+
                          ")<("+str(eksize)+","+str(pksize)+") and missing master secret key")
        else:
            run(eksize, pksize, True)
            return (eksize,pksize)
    else:
        return (curek,curpk)


if __name__ == "__main__":
    argeksize = int(sys.argv[1])
    argpksize = int(sys.argv[2])

    run(argeksize, argpksize, not os.path.isfile(options.get_mskey_file()))
