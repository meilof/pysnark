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

#include "modp.h"
#include "base.h"

using namespace std;

modp::modp() { val=0; }
modp::modp(const char* nm) { val=(mpz_class(nm)+qap_modulus) % qap_modulus; }
modp::modp(const string nm) { val=(mpz_class(nm)+qap_modulus) % qap_modulus; }
modp::modp(mpz_class& val0) { val=(qap_modulus+val0) % qap_modulus; }
modp::modp(int val0) { val=(mpz_class(val0)+qap_modulus) % qap_modulus; }

bool modp::operator==(int other) const { return val==other; }
bool modp::operator!=(modp other) const { return val!=other.val; }
modp modp::operator-() { modp ret; ret.val = qap_modulus-val; return ret; }
modp modp::operator+(modp other) { modp ret; ret.val = (val+other.val) % qap_modulus; return ret; }
modp modp::operator-(const modp& other) const { modp ret; ret.val = (val-other.val+qap_modulus) % qap_modulus; return ret; }
modp modp::operator-(int other) { modp ret; ret.val = (val-other+qap_modulus) % qap_modulus; return ret; }
modp& modp::operator+=(modp other) { val=(val+other.val) % qap_modulus; return *this; }
modp& modp::operator-=(modp& other) { val=(qap_modulus+val-other.val) % qap_modulus; return *this; }
modp& modp::operator-=(modp other) { val=(qap_modulus+val-other.val) % qap_modulus; return *this; }
//modp modp::operator*(modp& other) { modp ret; ret.val=(val*other.val) % qap_modulus; return ret; }
modp modp::operator*(const modp other) const { modp ret; ret.val=(val*other.val) % qap_modulus; return ret; }

modp modp::inv() {
    modp ret;
    mpz_invert(ret.val.get_mpz_t(), val.get_mpz_t(), qap_modulus.get_mpz_t());
    return ret;
}

modp operator*(mpz_class other, modp arg) {
  modp ret;
  ret.val = (arg.val*other) % qap_modulus;
  return ret;
}

modp modp::operator/(int other) {
    mpz_class ret = val/other;
    return modp(ret);
}

modp modp::operator^(const modp exp) const {
    mpz_class ret;
    mpz_powm(ret.get_mpz_t(), val.get_mpz_t(), exp.val.get_mpz_t(), qap_modulus.get_mpz_t());
    return modp(ret);
}

modp modp::operator^(unsigned int other) const {
    mpz_class ret;
    mpz_powm_ui(ret.get_mpz_t(), val.get_mpz_t(), other, qap_modulus.get_mpz_t());
    return modp(ret);
}


modp operator-(mpz_class other, modp arg) {
  modp ret;
  ret.val = (other-arg.val+qap_modulus) % qap_modulus;
  return ret;
}

void modp::operator--(int) {
  val = (val + qap_modulus - 1) % qap_modulus;
}

modp modp::rand() {
    mpz_class ret;
    mpz_urandomm(ret.get_mpz_t(), randst, qap_modulus.get_mpz_t());
    return modp(ret);
}

Ec1 operator^(const Ec1& orig, const modp arg) { return orig*arg.val; }
Ec2 operator^(const Ec2& orig, const modp arg) { return orig*arg.val; }

std::ostream& operator<<(std::ostream& os, const modp& x) {
    return os << x.val;
}

std::istream& operator>>(std::istream& is, modp& x) {
    string tok;
    is >> tok;
    x = modp(tok);
    return is;
}
