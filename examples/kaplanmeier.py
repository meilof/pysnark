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

from scipy.stats import chi2

from pysnark.runtime import Var
from pysnark.fixedpoint import VarFxp

import pysnark.prove

if __name__ == '__main__':
    # example batch of survival data from two populations
    kmdata = Var.vars([
        [ 0, 34, 0, 11 ], [ 0, 34, 0, 11 ], [ 0, 34, 0, 11 ], [ 0, 34, 0, 11 ],
        [ 0, 34, 0, 11 ], [ 0, 34, 0, 11 ], [ 0, 34, 0, 11 ], [ 0, 34, 0, 11 ],
        [ 1, 34, 0, 11 ], [ 0, 33, 0, 11 ], [ 0, 33, 0, 11 ], [ 0, 33, 1, 11 ],
        [ 0, 33, 1, 10 ], [ 0, 33, 0, 9 ], [ 1, 33, 0, 9 ], [ 0, 32, 0, 9 ],
        [ 0, 32, 0, 9 ], [ 0, 32, 0, 9 ], [ 0, 32, 0, 9 ], [ 1, 32, 0, 9 ],
        [ 0, 31, 0, 9 ], [ 0, 31, 0, 9 ], [ 0, 31, 0, 9 ], [ 1, 31, 0, 9 ],
        [ 0, 30, 0, 9 ], [ 0, 30, 0, 9 ], [ 1, 30, 0, 9 ], [ 0, 29, 1, 9 ],
        [ 0, 29, 0, 8 ], [ 0, 29, 0, 8 ], [ 0, 29, 0, 8 ], [ 0, 29, 1, 8 ],
        [ 0, 29, 0, 7 ], [ 0, 29, 0, 7 ], [ 0, 29, 0, 7 ], [ 1, 29, 0, 7 ],
        [ 1, 28, 0, 7 ], [ 0, 27, 0, 7 ], [ 0, 27, 0, 7 ], [ 0, 27, 0, 7 ],
        [ 1, 27, 0, 7 ], [ 0, 26, 0, 7 ], [ 0, 26, 0, 7 ], [ 0, 26, 0, 7 ],
        [ 0, 26, 0, 7 ], [ 0, 26, 1, 7 ], [ 1, 26, 0, 6 ], [ 0, 25, 0, 6 ],
        [ 0, 25, 0, 6 ], [ 0, 25, 0, 6 ], [ 1, 25, 0, 6 ], [ 0, 24, 0, 6 ],
        [ 0, 24, 0, 6 ], [ 0, 24, 0, 6 ], [ 0, 24, 0, 6 ], [ 0, 24, 0, 6 ],
        [ 0, 24, 0, 6 ], [ 0, 24, 0, 6 ], [ 0, 24, 0, 6 ], [ 0, 24, 0, 6 ],
        [ 0, 24, 0, 6 ], [ 0, 24, 0, 6 ], [ 0, 24, 1, 6 ], [ 1, 24, 0, 5 ],
        [ 0, 23, 0, 5 ], [ 1, 23, 0, 5 ], [ 1, 22, 1, 5 ], [ 1, 21, 0, 4 ],
        [ 0, 20, 0, 4 ], [ 0, 20, 0, 4 ], [ 0, 20, 0, 4 ], [ 0, 20, 0, 4 ],
        [ 0, 20, 0, 4 ], [ 0, 20, 0, 4 ], [ 0, 20, 0, 4 ], [ 1, 20, 0, 4 ],
        [ 0, 19, 0, 4 ], [ 0, 19, 0, 4 ], [ 0, 19, 1, 4 ], [ 0, 19, 0, 3 ],
        [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ],
        [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ],
        [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ],
        [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ],
        [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ],
        [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ],
        [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ],
        [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ],
        [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ],
        [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ],
        [ 0, 19, 0, 3 ], [ 0, 19, 0, 3 ], [ 0, 18, 0, 3 ], [ 0, 17, 0, 3 ],
        [ 0, 17, 0, 3 ], [ 0, 17, 0, 2 ], [ 0, 17, 0, 2 ], [ 0, 17, 0, 2 ],
        [ 0, 17, 0, 2 ], [ 0, 17, 0, 2 ], [ 0, 15, 0, 2 ], [ 0, 15, 0, 2 ],
        [ 0, 15, 0, 2 ], [ 0, 14, 0, 2 ], [ 0, 13, 0, 2 ], [ 0, 13, 0, 2 ],
        [ 0, 12, 0, 2 ], [ 0, 12, 0, 2 ], [ 0, 12, 0, 2 ], [ 0, 12, 0, 2 ],
        [ 0, 12, 0, 2 ], [ 0, 11, 0, 2 ], [ 0, 11, 0, 2 ], [ 0, 10, 0, 2 ],
        [ 0, 10, 0, 1 ], [ 0, 10, 0, 1 ], [ 0, 10, 0, 1 ], [ 0, 10, 0, 1 ],
        [ 0, 9, 0, 1 ], [ 0, 9, 0, 1 ], [ 0, 9, 0, 1 ], [ 0, 8, 0, 1 ],
        [ 0, 7, 0, 1 ], [ 0, 6, 0, 1 ], [ 0, 5, 0, 1 ], [ 0, 5, 0, 1 ],
        [ 0, 4, 0, 1 ], [ 0, 4, 0, 1 ], [ 0, 4, 0, 1 ], [ 0, 4, 0, 1 ],
        [ 0, 4, 0, 1 ], [ 0, 4, 0, 1 ], [ 0, 4, 0, 1 ], [ 0, 4, 0, 1 ],
        [ 0, 4, 0, 1 ], [ 0, 4, 0, 1 ], [ 0, 4, 0, 1 ], [ 0, 4, 0, 1 ],
        [ 0, 4, 0, 1 ], [ 0, 4, 0, 1 ], [ 0, 4, 0, 1 ], [ 0, 4, 0, 1 ],
        [ 0, 4, 0, 1 ], [ 0, 4, 0, 1 ], [ 0, 4, 0, 1 ]], "kmdata", 2)


    def step(di1,ni1,di2,ni2):
        frc = VarFxp.fromvar(di1+di2)/VarFxp.fromvar(ni1+ni2)
        ecur = frc*ni1
        v1n = VarFxp.fromvar(ni1 * ni2 * (di1+di2) * (ni1+ni2-di1-di2))
        v1d = VarFxp.fromvar((ni1+ni2) * (ni1+ni2) * (ni1+ni2-1))
        v1 = v1n/v1d
        return di1,ecur,v1

    steps = map(lambda x: step(*x), kmdata)
    (dtot,etot,vtot) = map(sum, zip(*steps))

    dtot = VarFxp.fromvar(dtot)
    chi0 = (dtot - etot)
    chi = chi0*chi0/vtot
    chi = chi.val()

    print "Final result: chi statistic=", chi, ", p-value=", 1 - chi2.cdf(chi, 1)
