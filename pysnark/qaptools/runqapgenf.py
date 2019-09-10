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

import os.path
import subprocess
import sys

import pysnark.options as psopt

def get_ekfile_sig(ekfile):
    """
    Get function signature from evaluation key file

    :param ekfile: Evaluation key file
    :return: Function signature (first token in the file), or empty string if file does not exist
    """

    if not os.path.exists(ekfile): return ""

    ekf = open(ekfile)
    cursig = ekf.next().strip().split(" ")[0]
    ekf.close()
    return cursig


def run(nm, sig, sz=None):
    """
    Run the qapgenf tool to generate evaluation/verification keys for the given function.

    :param nm: Function name to generate key material for
    :param sig: Signature of the function (as returned by :py:fn:`pysnark.qapsplit.qapsplit`
    :param sz: If None, use the master secret key; else, use the coefficient cache of the given size
    :return: None
    """
    if subprocess.call([psopt.get_qaptool_exe("qapgenf"),
                        psopt.get_mkey_file(),
                        psopt.get_mskey_file() if sz is None else psopt.get_cache_file(sz),
                        psopt.get_eqs_file_fn(nm),
                        psopt.get_ek_file(nm),
                        psopt.get_vk_file(nm),
                        sig]) != 0:
        sys.exit(2)


def ensure_ek(nm, sig, eksz):
    """
    Ensure that up-to-date evaluation key for the function is available,
    corresponding to the given signature

    :param nm: Function name
    :param sig: Signature as returned by :py:fn:`pysnark.qapsplit.qapsplit`
    :param eksz: Function size as returned by :py:fn:`pysnark.qapsplit.qapsplit`
    :return: None
    """

    if get_ekfile_sig(psopt.get_ek_file(nm)) == sig:
        return

    print("New signature for function " + str(nm) + ", rebuilding keys", file=sys.stderr)

    if os.path.isfile(psopt.get_mskey_file()):
        run(nm, sig, None)
    else:
        cachefile = psopt.get_cache_file(eksz)
        if not os.path.isfile(cachefile):
            print("*** Generating coefficient cache without master secret key: this may be slow...", file=sys.stderr)
            outf = open(cachefile, "w")
            ret = subprocess.call([psopt.get_qaptool_exe("qapcoeffcache"), psopt.get_mkey_file(), str(eksz)], stdout=outf)
            outf.close()
            if ret != 0: sys.exit(2)

        run(nm, sig, eksz)
