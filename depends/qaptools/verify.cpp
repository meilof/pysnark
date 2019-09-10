/**
 * Copyright (c) 2016-2018 Koninklijke Philips N.V. All rights reserved. A
 * copyright license for redistribution and use in source and binary forms,
 * with or without modification, is hereby granted for non-commercial,
 * experimental and research purposes, provided that the following conditions
 * are met:
 * - Redistributions of source code must retain the above copyright notice,
 *   this list of conditions and the following disclaimers.
 * - Redistributions in binary form must reproduce the above copyright notice,
 *   this list of conditions and the following disclaimers in the
 *   documentation and/or other materials provided with the distribution. If
 *   you wish to use this software commercially, kindly contact
 *   info.licensing@philips.com to obtain a commercial license.
 *
 * This license extends only to copyright and does not include or grant any
 * patent license or other license whatsoever.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

#include <fstream>
#include <set>

#include "base.h"
#include "qap.h"
#include "verify.h"

using namespace std;

bool qapblockvalid(const masterkey& mk, const datablock& db) {
    Fp12 e1, e2, e3;

    if (!db.comm.isValid() || !db.commal.isValid()) {
        cerr << "*** Invalid points in data block" << endl;
        return false;
    }

    // alpha check
    opt_atePairing(e1, mk.g_al, db.comm);
    opt_atePairing(e2, db.commal, g1);
    if (e1!=e2) { cerr << "*** c-alpha pairing check failed" << endl;  }

    return true;
}

bool qapblockver(const masterkey& mk, const datablock& db, const blockvk& bvk, const blockproof& block) {
    Fp12 e1, e2, e3;

    if (!block.comm.isValid() || !block.commal.isValid() || !block.commz.isValid()) {
        cerr << "*** Invalid points in block" << endl;
        return false;
    }

    // alpha' check
    opt_atePairing(e1, bvk.g2al, block.comm);
    opt_atePairing(e2, block.commal, g1);
    if (e1!=e2) { cerr << "*** c'-alpha pairing check failed" << endl;  }

    // z check
    opt_atePairing(e1, bvk.g2beta, db.comm + block.comm);
    opt_atePairing(e2, g2, block.commz);
    if (e1!=e2) { cerr << "*** block z pairing check failed" << endl;  }

    return true;
}

bool qapver(const qapvk& qvk, const qapproof& proof, const wirevalt& pubwires, string prefix) {
    Fp12 e1, e2, e3;


    if (!proof.p_rvx.isValid() || !proof.p_ravx.isValid() ||
        !proof.p_rwx.isValid() || !proof.p_rawx.isValid() ||
        !proof.p_ryx.isValid() || !proof.p_rayx.isValid() ||
        !proof.p_z.isValid()   || !proof.p_h.isValid()) {
        cerr << "*** Invalid points in proof" << endl;
        return false;
    }

    // alpha checks
    opt_atePairing(e1, proof.p_ravx, g1);
    opt_atePairing(e2, qvk.g2alv, proof.p_rvx);
    if (e1!=e2) { cerr << "*** p_ravx pairing check failed" << endl;  }

    opt_atePairing(e1, g2, proof.p_rawx);
    opt_atePairing(e2, proof.p_rwx, qvk.g1alw);
    if (e1!=e2) { cerr << "*** p_rawx pairing check failed" << endl;  }

    opt_atePairing(e1, proof.p_rayx, g1);
    opt_atePairing(e2, qvk.g2aly, proof.p_ryx);
    if (e1!=e2) { cerr << "*** p_rayx pairing check failed" << endl;  }

    // s check
    Ec1 versum = proof.p_rvx+proof.p_ryx;
    for (auto const& it: proof.blocks) versum += it.second.comm;
    opt_atePairing(e1, g2, proof.p_z);
    opt_atePairing(e2, qvk.g2bet, versum);
    opt_atePairing(e3, proof.p_rwx, qvk.g1bet);
    if (e1!=(e2*e3)) { cerr << "*** beta check failed" << endl;  }

    Ec1 pub_rvx = g10;
    Ec2 pub_rwx = g20;
    Ec1 pub_ryx = g10;

    for (auto const& it: qvk.pubinputs) {
        modp val = it.first == "one" ? 1 : pubwires.at(prefix+"/"+it.first);
        //cerr << "including " << it.first << "=" << val << endl;
        pub_rvx += it.second.g_rvvk^val;
        pub_rwx += it.second.g_rwwk^val;
        pub_ryx += it.second.g_ryyk^val;
    }

    opt_atePairing(e1, pub_rwx + proof.p_rwx, pub_rvx + proof.p_rvx);
    opt_atePairing(e2, qvk.g2ryt, proof.p_h);
    opt_atePairing(e3, g2, pub_ryx + proof.p_ryx);
    if (e1!=(e2*e3)) { cerr << "*** divisibility check failed" << endl;  }

    return true;
}
