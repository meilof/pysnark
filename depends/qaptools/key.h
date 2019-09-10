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
#include <unordered_set>

using namespace std;

#include <gmpxx.h>
#define MIE_ATE_USE_GMP
#include <bn.h>
using namespace bn;

#include "modp.h"

class mastersk {
  public:
    modp s;
    modp rc;
    modp al;
};

std::ostream& operator<<(std::ostream& os, const mastersk& x);

std::istream& operator>>(std::istream& is, mastersk& x);

class masterkey {
  public:
    vector<Ec1> g_s;      // first one: g^0
    vector<Ec2> g2_s;      // first one: g^0

    Ec2 g_al;    // al
    vector<Ec1> g_rcs;
    vector<Ec2> g_rcals;
};

std::ostream& projectmk(std::ostream& os, const masterkey& x, unsigned int maxpower);

std::ostream& operator<<(std::ostream& os, const masterkey& x);

std::istream& operator>>(std::istream& is, masterkey& x);

class coeffcache {
  public:
    vector<Ec1> g1_coeff;
    vector<Ec2> g2_coeff;
};

std::ostream& operator<<(std::ostream& os, const coeffcache& x);

std::istream& operator>>(std::istream& is, coeffcache& x);


class wirevk { // wire verification key (for public wires)
public:
    Ec1 g_rvvk;
    Ec2 g_rwwk;
    Ec1 g_ryyk;
};

class wireek : public wirevk { // wire evaluation key (for non-public wires)
public:
    Ec2 g_rvavvk;
    Ec1 g_rwawwk;
    Ec2 g_ryayyk;
    Ec1 g_rvvkrwwkryyk;
};


class blockvk {
public:
    Ec2 g2al;
    Ec2 g2beta;
};

class blockek {
public:
    vector<Ec2> g2als;            // no randomness before!
    vector<Ec1> g1betas;          // no randomness before!
    Ec2 g2al;
    Ec1 g1betar1, g1betar2;
    int gstart;                   // start in gs of first value (e.g., 1)
};

class qapvk {
public:
    //wirevk constwire;

    Ec2 g2alv;
    Ec1 g1alw;
    Ec2 g2aly;
    Ec2 g2ryt;

    Ec1 g1bet;
    Ec2 g2bet;

    map<string,blockvk> blocks;
    map<string,wirevk> pubinputs;
};

class qapek {
public:
    Ec1 g_rvt, g_rwawt, g_ryt;
    Ec2 g_rvavt, g2_rwt, g_ryayt;

    Ec1 g_beta, g_rvbt, g_rwbt, g_rybt;

    map<string,blockek> blocks;
    map<string,wireek> wires;
};


std::ostream& operator<<(std::ostream& os, const wireek& ek);
std::istream& operator>>(std::istream& in, wireek& ek);

std::ostream& operator<<(std::ostream& os, const qapvk& x);
std::istream& operator>>(std::istream& is, qapvk& x);

std::ostream& operator<<(std::ostream& os, const qapek& x);
std::istream& operator>>(std::istream& is, qapek& x);
