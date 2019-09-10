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

    if (argc!=7) {
        cerr << "Usage: qapgenf <mkeyfile> <mskfile>|<coeffcachefile> <qapfile> <ekfile> <vkfile> <sig>" << endl;
        return 2;
    }

    masterkey mkey;
    ifstream mkeyfile(argv[1]);
    mkeyfile >> mkey;
    mkeyfile.close();
    
    mastersk sk; modp* sptr = NULL;
    coeffcache ca; coeffcache* captr = NULL;
    
    ifstream inkeypeek(argv[2]);
    string type;
    inkeypeek >> type;
    inkeypeek.close();

    ifstream mfile(argv[2]);
    if (type == "geppetri_mastersk") {
        mfile >> sk;
        sptr = &sk.s;
        cerr << "Generating functon key material using master secret key" << endl;
    } else if (type == "geppetri_coeffcache") {
        mfile >> ca;
        captr = &ca;
        cerr << "Generating functon key material using coefficient cache" << endl;
    } else {
        cerr << "*** Error: file " << argv[2] << " is not a master secret key or coefficient cache" << endl;
        return 2;
    }
    mfile.close();

    cerr << "Reading QAP..." << endl;

    qap q;
    ifstream qapfile(argv[3]); 
    qapfile >> q;

    cerr << "Generating keys..." << endl;

    qapek ek;
    qapvk vk;
    qap2key(q, mkey, sptr, captr, ek, vk);

    cerr << "Writing to " << argv[4] << endl;

    ofstream qapo1(argv[4]);
    qapo1 << argv[6] << " " << ek << endl;
    qapo1.close();

    cerr << "Writing to " << argv[5] << endl;

    ofstream qapo2(argv[5]);
    qapo2 << argv[6] << " " << vk << endl;
    qapo2.close();


    return 0;
}
