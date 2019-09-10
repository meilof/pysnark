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

#include "base.h"
#include "modp.h"
#include "key.h"
#include "proof.h"

#include <fstream>
using namespace std;

datablock::datablock() {
    comm = g10;
    commal = g20;
}

datablock operator+(const datablock& b1, const datablock& b2) {
    datablock ret;
    ret.comm = b1.comm + b2.comm;
    ret.commal = b1.commal + b2.commal;
    return ret;
}


datablock operator*(modp fac, datablock orig) {
    datablock ret;
    ret.comm = orig.comm^fac;
    ret.commal = orig.commal^fac;
    return ret;
}

datablock operator-(datablock p1, datablock p2) {
    return p1 + -1*p2;
}


std::ostream& operator<<(std::ostream& os, const datablock& x) {
    os << "geppetri_datablock [ " << x.comm << " " << x.commal << " ]";
    return os;
}

std::istream& operator>>(std::istream& is, datablock& x) {
    string checktok; is >> checktok;
    if (checktok != "geppetri_datablock") throw std::ios_base::failure((string("Expected \"geppetri_datablock\", got \"") + checktok + "\"").c_str());

    char br; is >> br;
    if (br != '[') throw std::ios_base::failure((string("Bad datablock: expected \"[\", got \"") + br + "\"").c_str());

    is >> x.comm >> x.commal;

    is >> br;
    if (br != ']') throw std::ios_base::failure((string("Bad datablock: expected \"]\", got \"") + br + "\"").c_str());
    return is;
}

blockproof::blockproof() {
    comm = g10;
    commal = g20;
    commz = g10;
}

std::ostream& operator<<(std::ostream& os, const blockproof& x) {
    os << "[ " << x.comm << " " << x.commal << " " << x.commz << " ]";
    return os;
}

std::istream& operator>>(std::istream& is, blockproof& x) {
    char br; is >> br;
    if (br != '[') throw std::ios_base::failure((string("Bad blockproof: expected \"[\", got \"") + br + "\"").c_str());

    is >> x.comm >> x.commal >> x.commz;

    is >> br;
    if (br != ']') throw std::ios_base::failure((string("Bad blockproof: expected \"]\", got \"") + br + "\"").c_str());
    return is;
}

qapproof::qapproof() {
    p_rvx = g10;
    p_rwx = g20;
    p_ryx = g10;
    p_ravx = g20;
    p_rawx = g10;
    p_rayx = g20;
    p_z = g10;
}

std::ostream& operator<<(std::ostream& os, const qapproof& x) {
    os << "geppetri_qapproof [ " << endl;
    os << "  " << x.p_rvx << endl;
    os << "  " << x.p_rwx << endl;
    os << "  " << x.p_ryx << endl;
    os << "  " << x.p_ravx << endl;
    os << "  " << x.p_rawx << endl;
    os << "  " << x.p_rayx << endl;
    os << "  " << x.p_z << endl;
    os << "  " << x.p_h << endl;
    for (auto const& it: x.blocks) {
        os << "  " << it.first << " " << it.second << endl;
    }
    os << "]" << endl;
    return os;
}

std::istream& operator>>(std::istream& is, qapproof& x) {
    string checktok; is >> checktok;
    if (checktok != "geppetri_qapproof") throw std::ios_base::failure((string("Expected \"geppetri_qapproof\", got \"") + checktok + "\"").c_str());

    char br; is >> br;
    if (br != '[') throw std::ios_base::failure((string("Bad qapproof: expected \"[\", got \"") + br + "\"").c_str());

    is >> x.p_rvx >> x.p_rwx >> x.p_ryx >> x.p_ravx >> x.p_rawx >> x.p_rayx >> x.p_z >> x.p_h;

    string tok;

    while (!(is>>tok).eof() && tok!="]") {
//        cerr << "reading block " << tok << endl;
        is >> x.blocks[tok];
    }

    if (tok != "]") throw std::ios_base::failure((string("Bad qapproof: expected \"]\", got \"") + br + "\"").c_str());
    return is;
}

blockproof operator*(modp fac, blockproof orig) {
    blockproof ret;
    ret.comm = orig.comm^fac;
    ret.commal = orig.commal^fac;
    ret.commz = orig.commz^fac;
    return ret;
}

blockproof operator-(blockproof p1, blockproof p2) {
    return p1+(-1)*p2;
}

blockproof operator+(blockproof p1, blockproof p2) {
    blockproof ret;
    ret.comm = p1.comm + p2.comm;
    ret.commal = p1.commal + p2.commal;
    ret.commz = p1.commz + p2.commz;
    return ret;

}


qapproof operator*(modp fac, qapproof orig) {
    qapproof ret;
    for (auto const& it: orig.blocks) ret.blocks[it.first]=fac*it.second;
    ret.p_rvx = orig.p_rvx^fac;
    ret.p_rwx = orig.p_rwx^fac;
    ret.p_ryx = orig.p_ryx^fac;
    ret.p_ravx = orig.p_ravx^fac;
    ret.p_rawx = orig.p_rawx^fac;
    ret.p_rayx = orig.p_rayx^fac;
    ret.p_z = orig.p_z^fac;
    ret.p_h = orig.p_h^fac;
    return ret;
}

qapproof operator-(qapproof p1, qapproof p2) {
    return p1+(-1)*p2;
}

qapproof operator+(qapproof p1, qapproof p2) {
    qapproof ret;
    for (auto const& it: p1.blocks) ret.blocks[it.first]=it.second+p2.blocks[it.first];
    ret.p_rvx = p1.p_rvx+p2.p_rvx;
    ret.p_rwx = p1.p_rwx+p2.p_rwx;
    ret.p_ryx = p1.p_ryx+p2.p_ryx;
    ret.p_ravx = p1.p_ravx+p2.p_ravx;
    ret.p_rawx = p1.p_rawx+p2.p_rawx;
    ret.p_rayx = p1.p_rayx+p2.p_rayx;
    ret.p_z = p1.p_z+p2.p_z;
    ret.p_h = p1.p_h+p2.p_h;
    return ret;
}
