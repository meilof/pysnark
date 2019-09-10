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

#include <cstdlib>
#include <fstream>
#include <time.h>

#include "base.h"
#include "key.h"
#include "modp.h"
#include "proof.h"
#include "prove.h"
#include "qap.h"

#include <getopt.h>


template<typename X> X readfromfile(string fname, bool skiptok = false) {
    X ret;
    ifstream fl(fname);
    if (!fl.is_open()) {
        cerr << "*** Could not open file " << fname << endl;
        exit(1);
    }
    if (skiptok) {
        string tok;
        fl >> tok;
    }
    fl >> ret;
    fl.close();
    return ret;
}

int main (int argc, char **argv) {
    libqap_init();

    if (argc != 5) {
        cerr << "Usage: " << argv[0] << " <mkeyfile> <wirefile> <iofile> <schedule>" << endl;
        return 2;
    }

    masterkey mkey = readfromfile<masterkey>(argv[1]);
    wirevalt wirevals = readfromfile<wirevalt>(argv[2]);
    wirevalt pubvals = readfromfile<wirevalt>(argv[3]);
    for (auto const& it: pubvals) wirevals[it.first] = it.second;

    map<string,qap> qaps;
    map<string,qapek> qapeks;

    ifstream sched(argv[4]);
    if (!sched.is_open()) {
        cerr << "*** Could not open schedule file " << argv[4] << endl;
        return 2;
    }

    map<string,string> qap2type;

    while (!sched.eof()) {
        string tok;

        sched >> tok;

        if (tok=="") continue;

        if (tok == "[function]") {
            //string type; sched >> type;
            string name; sched >> name;
            string eqfile; sched >> eqfile;
            string ekfile; sched >> ekfile;
            string vkfile; sched >> vkfile;
            qap2type[name] = ekfile;

            if (qaps.find(ekfile) == qaps.end()) {
                cerr << "Reading QAP from (" << eqfile << "," << ekfile << ")" << endl;
                qaps[ekfile] = readfromfile<qap>(eqfile);
                qapeks[ekfile] = readfromfile<qapek>(ekfile, true);
            }

            qap& theqap = qaps[ekfile];
            qapek& theek = qapeks[ekfile];

            cerr << "Proving " << name << " (" << ekfile << ")" << endl;
            qapproof proof = qapprove(mkey, theqap, theek, wirevals, name, true);

            for (auto const& it: theek.blocks) {
                proof.blocks[it.first] = qapblockproof(mkey, it.second, qaps[ekfile].blocks[it.first],
                                                       name, wirevals,
                                                       wirevals.at(name+"/rnd1_" + it.first),
                                                       wirevals.at(name+"/rnd2_" + it.first)
                                                      );
            }

            cout << proof;
        } else if (tok=="[external]") {
            string fun; sched >> fun;
            string type = qap2type[fun];
            string blk; sched >> blk;
            string blkwires; sched >> blkwires;
            string blkfile; sched >> blkfile;
        } else if (tok=="[glue]") {
            string fun1; sched >> fun1;
            string type1 = qap2type[fun1];
            string blk1; sched >> blk1;
            string fun2; sched >> fun2;
            string type2 = qap2type[fun2];
            string blk2; sched >> blk2;

            cout << buildblock(mkey, qaps[type1].blocks[blk1], fun1, wirevals, wirevals.at(fun1+"/rnd1_"+blk1)) << endl;
        } else {
            cerr << "*** Unrecognized token: " << tok << endl;
        }
    }

    return 0;
}
