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

#include "qap.h"
#include "base.h"

#include <fstream>


std::istream& operator>>(std::istream& is, qapeq& eq) {
    string tok;

    while ((is>>tok) && tok != "*") {
        coeff co;
        co.co = modp(tok);

        is >> tok;
        co.te = tok;

        eq.v.push_back(co);
    }

    while ((is>>tok) && tok != "=") {
        coeff co;
        co.co = modp(tok);

        is >> tok;
        co.te = tok;

        eq.w.push_back(co);
    }

    while (is.peek() !='\n' && is>>tok) {
        if (tok==".") return is;

        coeff co;
        co.co = modp(tok);

        is >> tok;
        co.te = tok;

        eq.y.push_back(co);
    }

    return is;
}

std::istream& operator>>(std::istream& is, qap& qap) {
    while (!is.eof()) {
        string btp;
        getline(is,btp);
        if (btp == "" || btp.c_str()[0] == '#') continue;
        stringstream ss(btp);

        if (ss.peek() == '[') {
            // special command
            string tok; ss >> tok;

            if (tok == "[ioblock]") {
                string nm; ss >> nm;
                block bl;
                while (!ss.eof()) {
                    ss >> tok;
                    bl.push_back(tok);
                }
                qap.blocks[nm] = bl;
            }
        } else {
            qapeq nw;
            ss >> nw;
            qap.eqs.push_back(nw);
        }
    }


    return is;
}


istream& operator>>(istream& is, wirevalt& x) {
    while (!is.eof()) {
        string btp;
        getline(is,btp);
        if (btp == "" || btp.c_str()[0] == '#') continue;
        stringstream ss(btp);

        string tok;
        ss >> tok;
        if (tok=="" || tok.substr(tok.size()-1)!=":") throw std::ios_base::failure((string("Expected wire name:").c_str()));
        tok=tok.substr(0, tok.size()-1);
        ss >> x[tok];
    }
    return is;
}
