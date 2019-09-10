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

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <getopt.h>
#include <time.h>

#include "base.h"
#include "key.h"
#include "proof.h"
#include "prove.h"
#include "qap2key.h"

using namespace std;


int main(int argc, char** argv) {
    libqap_init();

    if (argc!=3) {
        cerr << "*** Usage: " << argv[0] << " <mkeyfile> <datafile>" << endl;
        return 2;
    }

    cerr << "Building commitment: keyfile=" << argv[1] << ", datafile=" << argv[2] << endl;

    masterkey mkey;
    ifstream fkeyfile(argv[1]);
    fkeyfile >> mkey;
    fkeyfile.close();

    vector<modp> vals;
    ifstream fdatafile(argv[2]);
    string tok;
    while ((fdatafile>>tok) && tok!="") {
        vals.push_back(modp(tok));
    }
    fdatafile.close();

    modp rnd = modp(vals.back());
    vals.pop_back();

    datablock db = buildblock(mkey, vals, rnd);

    cout << db << endl;

    return 0;
}
