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

#include <gmpxx.h>
#define MIE_ATE_USE_GMP
#include <bn.h>

using namespace bn;
using namespace std;

gmp_randstate_t randst;
mpz_class qap_modulus;
Ec1 g1, g10;
Ec2 g2, g20;

void libqap_init() {
  CurveParam cp = CurveSNARK1;
  cp.b = 3;
  Param::init(cp);
  qap_modulus = mpz_class(Param::r.toString());

  g1=Ec1(1, 2);
  g10=g1*0;
  g2=Ec2(Fp2(Fp("10857046999023057135944570762232829481370756359578518086990519993285655852781"),
             Fp("11559732032986387107991004021392285783925812861821192530917403151452391805634")),
         Fp2(Fp("8495653923123431417604973247489272438418190587263600148770280649306958101930"),
             Fp("4082367875863433681332203403145435568316851327593401208105741076214120093531")));
  g20=g2*0;

  gmp_randinit_default (randst);
}

