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

#include <gmpxx.h>
#define MIE_ATE_USE_GMP
#include <bn.h>
using namespace bn;

class modp {
  public:
    modp();
    modp(const char* nm);
    modp(const std::string nm);
    modp(mpz_class& val0);
    modp(int val0);

    bool operator==(int other) const;
    bool operator!=(modp other) const;
    modp operator-();
    modp operator+(modp other);
    modp operator-(const modp& other) const;
    modp operator-(int other);
    modp& operator+=(modp other);
    modp& operator-=(modp& other);
    modp& operator-=(modp other);
//    modp operator*(modp& other);
    modp operator*(const modp other) const;
    modp operator/(int other);     // assume integral result
    modp operator^(const modp other) const;
    modp operator^(unsigned int other) const;
    void operator--(int);

    modp inv();
    static modp rand();

    mpz_class val;
};

modp operator*(mpz_class other, modp arg);
modp operator-(mpz_class other, modp arg);
std::ostream& operator<<(std::ostream& str, const modp& arg);
Ec1 operator^(const Ec1& orig, const modp arg);
Ec2 operator^(const Ec2& orig, const modp arg);

std::ostream& operator<<(std::ostream& os, const modp& x);
std::istream& operator>>(std::istream& is, modp& x);
