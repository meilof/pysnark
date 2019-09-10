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

#pragma once

#include <map>

using namespace std;

#include <gmpxx.h>
#define MIE_ATE_USE_GMP
#include <bn.h>
using namespace bn;

#include "modp.h"

class datablock {
public:
    datablock();

    Ec1 comm;
    Ec2 commal;
};

datablock operator*(modp fac, datablock orig);
datablock operator-(datablock p1, datablock p2);

std::ostream& operator<<(std::ostream& os, const datablock& x);
std::istream& operator>>(std::istream& is, datablock& x);

datablock operator+(const datablock& b1, const datablock& b2);


class blockproof {
public:
    blockproof();

    Ec1 comm;
    Ec2 commal;
    Ec1 commz;
};

std::ostream& operator<<(std::ostream& os, const blockproof& x);
std::istream& operator>>(std::istream& is, blockproof& x);

blockproof operator*(modp fac, blockproof orig);
blockproof operator-(blockproof p1, blockproof p2);
blockproof operator+(blockproof p1, blockproof p2);

class qapproof {
public:
    qapproof();

    map<string,blockproof> blocks;

    Ec1 p_rvx;
    Ec2 p_rwx;
    Ec1 p_ryx;
    Ec2 p_ravx;
    Ec1 p_rawx;
    Ec2 p_rayx;
    Ec1 p_z;
    Ec1 p_h;
};

qapproof operator*(modp fac, qapproof orig);
qapproof operator-(qapproof p1, qapproof p2);
qapproof operator+(qapproof p1, qapproof p2);

std::ostream& operator<<(std::ostream& os, const qapproof& x);
std::istream& operator>>(std::istream& is, qapproof& x);

