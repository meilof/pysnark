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
#include <map>
#include <set>
#include <time.h>

#include "base.h"
#include "key.h"
#include "prove.h" // TODO: eliminate this include
#include "proof.h"
#include "verify.h"

using namespace std;

// TODO: move to common lib
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

//bool qapblockver(const masterkey& mk, const datablock& db, const qapvk& qvk, const blockvk& bvk, const blockproof& block);
//bool qapver(const qapvk& qvk, const qapproof& proof);

int main (int argc, char **argv) {
    libqap_init();

    if (argc!=5) {
        cerr << "Usage: " << argv[0] << "<masterkey> <schedule> <proof> <iowires>" << endl;
        return 2;
    }

    masterkey mkey = readfromfile<masterkey>(argv[1]);
    ifstream sched(argv[2]);
    ifstream prooff(argv[3]);
    wirevalt wirevals = readfromfile<wirevalt>(argv[4]);

    map<string,string> qap2type;
    map<string,qapvk> qapvks;
    map<string,qapproof> proofs;

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
            qap2type[name] = vkfile;

            if (qapvks.find(vkfile) == qapvks.end()) {
                cerr << "Reading QAP vk: " << vkfile << endl;
                qapvks[vkfile] = readfromfile<qapvk>(vkfile, true);
            }

            cerr << "Verifying " << name << " (" << vkfile << ")" << " ";
            prooff >> proofs[name];
            cerr << qapver(qapvks[vkfile], proofs[name], wirevals, name) << endl;
        } else if (tok=="[external]") {
            string fun; sched >> fun;
            string type = qap2type[fun];
            string blk; sched >> blk;
            string blkwires; sched >> blkwires;
            string blkfile; sched >> blkfile;

            cerr << "Reading input block file " << blkfile << endl;
            datablock din = readfromfile<datablock>(blkfile);

            cerr << "Verifying input block " << fun << " " << blk << " ";
            cerr << qapblockvalid(mkey, din) << " ";
            cout << qapblockver(mkey, din, qapvks[type].blocks[blk], proofs[fun].blocks[blk]) << endl;
        } else if (tok=="[glue]") {
            string fun1; sched >> fun1;
            string type1 = qap2type[fun1];
            string blk1; sched >> blk1;
            string fun2; sched >> fun2;
            string type2 = qap2type[fun2];
            string blk2; sched >> blk2;

            datablock blk; prooff >> blk;

            cerr << "Verifying glue " << fun1 << "." << blk1 << "<->" << fun2 << "." << blk2 << " ";
            cerr << qapblockvalid(mkey, blk) << " ";
            cerr << qapblockver(mkey, blk, qapvks[type1].blocks[blk1], proofs[fun1].blocks[blk1]) << " ";
            cerr << qapblockver(mkey, blk, qapvks[type2].blocks[blk2], proofs[fun2].blocks[blk2]) << endl;
        } else {
            cerr << "*** Unrecognized token: " << tok << endl;
        }
    }

    return 0;
}


