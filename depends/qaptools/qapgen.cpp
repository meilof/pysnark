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

    if (argc != 6) {
        cerr << "*** Usage: " << argv[0] << "<sz> <pksz> [+]<skfile> <ekfile> <pkfile>" << endl;
        return 2;
    }

    mastersk sk;
    int fac;
    if (argv[3][0] == '+') {
        // extend based on previous master sk
        cerr << "Extending/rebuilding keys based on existing mastersk" << endl;
        ifstream skfile(argv[3]+1);
        skfile >> sk;
        skfile.close();
    } else {
        // generate new master sk
        cerr << "Generating new mastersk and keys" << endl;
        generate_master_skey(sk);
        ofstream skfile(argv[3]);
        skfile << sk;
        skfile.close();
    }

    masterkey mk;
    int maxqaplen = atoi(argv[1]);
    generate_master_key(sk, maxqaplen, mk);

    ofstream ekfile(argv[4]);
    ekfile << mk;
    ekfile.close();

    ofstream pkfile(argv[5]);
    int maxpublen = atoi(argv[2]);
    if (maxpublen > maxqaplen) {
        cerr << "*** maxqaplen should be a at least " << maxqaplen << ", is " << maxpublen << endl;
        return 2;
    }
    projectmk(pkfile, mk, maxpublen);
    pkfile.close();

    cerr << "done" << endl;

    return 0;
}
