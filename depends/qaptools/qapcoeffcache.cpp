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
#include <getopt.h>

#include "base.h"
#include "qap.h"
#include "qap2key.h"

#include <gmpxx.h>
#define MIE_ATE_USE_GMP
#include <bn.h>

using namespace bn;


int main(int argc, char** argv) {
    libqap_init();

    if (argc!=3) {
        cerr << "Usage: qapcoeffcache <mkeyfile>|<ekfile> <size>" << endl;
        return 2;
    }

    ifstream inkeypeek(argv[1]);
    string type;
    inkeypeek >> type;
    inkeypeek.close();

    coeffcache cache;
    int sz = atoi(argv[2]);

    if (type == "geppetri_masterkey") {
        masterkey mkey;
        ifstream mkeyfile(argv[1]);
        mkeyfile >> mkey;
        mkeyfile.close();

        if (mkey.g_s.size()-1<sz) {
            cerr << "*** Master key too small to generate cache: " << mkey.g_s.size() << "-1 < " << sz << endl;
            return 2;
        }

        generate_coeff_cache(mkey, sz, cache);
        cout << cache << endl;
    } else if (type == "geppetri_mastersk") {
        mastersk msk;
        ifstream mskfile(argv[1]);
        mskfile >> msk;
        mskfile.close();

        generate_coeff_cache(msk, sz, cache);
        cout << cache << endl;
    } else {
        cerr << "*** Incorrect input file for " << argv[0] << ": expected master secret key/master key, got " << type;
        return 2;
    }


    return 0;
}
