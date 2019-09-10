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
#include "fft.h"
#include "key.h"
#include "prove.h"
#include "qap.h"

datablock buildblock(const masterkey& mk, const vector<modp>& vals, modp rnd) {
    datablock ret;

//    cerr << "[buildblock']" << endl;
//    cerr << "Randomness " << rnd << "; inputter=" << inputter << endl;

    ret.comm = mk.g_rcs[0]^rnd;
    ret.commal = mk.g_rcals[0]^rnd;

    for (unsigned int i = 0; i < vals.size(); i++) {
//        cerr << "val " << vals[i] << " at rcs " << (i+1) << endl;
        ret.comm += mk.g_rcs[i+1]^vals[i];
        ret.commal += mk.g_rcals[i+1]^vals[i];
    }

    return ret;
}

datablock buildblock(const masterkey& mkey, const block& wires, const string prefix, const wirevalt& wirevals, const modp r1) {
    datablock ret;

    ret.comm    = mkey.g_rcs[0]^r1;
    ret.commal  = mkey.g_rcals[0]^r1;


    int ix = 0;
    for (auto const& it: wires) {
        modp val = wirevals.at(prefix+"/"+it);
        ret.comm += mkey.g_rcs[ix+1]^val;
        ret.commal += mkey.g_rcals[ix+1]^val;

        ix++;
    }

    return ret;
}

blockproof qapblockproof(const masterkey& mkey, const blockek& ek, const block& blk, string prefix, const wirevalt& wirevals, const modp r1, const modp r2) {
    blockproof ret;

    ret.comm    = mkey.g_s[0]^r2;
    ret.commal  = ek.g2al^r2;
    ret.commz   = ek.g1betar1^r1;
    ret.commz  += ek.g1betar2^r2;

    int ix = 0;
    for (auto const& it: blk) {
        modp val = wirevals.at(prefix+"/"+it);
        ret.comm += mkey.g_s[ek.gstart+ix]^val;
        ret.commal += ek.g2als[ix]^val;
        ret.commz += ek.g1betas[ix]^val;
        ix++;
    }

    return ret;
}

 blockproof qappubblock(const masterkey& mkey, const blockek& ek, const block& blk, string prefix, const wirevalt& wirevals, const modp r2) {
    blockproof ret;
    int ix = 0;

    ret.comm += mkey.g_s[0]^r2;

    for (auto const& it: blk) {
        modp val = wirevals.at(prefix+"/"+it);
        ret.comm += mkey.g_s[ek.gstart+ix]^val;
        ix++;
    }

    return ret;
}



void computevwyval(const vector<qapeq>& eqs,
                   string prefix, const wirevalt& vals,
                   vector<modp>& vval, vector<modp>& wval, vector<modp>& yval,
                   bool check) {
    int ix = 0;
    for (auto const& eq: eqs) {
        // TODO: slight optimization: if v or w is empty, then no need to evaluate any of them!
        for (auto const& vcur: eq.v) vval[ix]+=vcur.co*(vcur.te=="one"?1:vals.at(prefix+"/"+vcur.te));
        for (auto const& wcur: eq.w) wval[ix]+=wcur.co*(wcur.te=="one"?1:vals.at(prefix+"/"+wcur.te));
        if (check || eq.v.size()!=0 || eq.w.size()!=0) for (auto const& ycur: eq.y)
            yval[ix]+=ycur.co*(ycur.te=="one"?1:vals.at(prefix+"/"+ycur.te));
        if (check && vval[ix]*wval[ix] != yval[ix])
            cerr << "*** Eq not satisfied @ " << (ix+1) << ": " << vval[ix] << "*" << wval[ix] << "=" << vval[ix]*wval[ix] << " != " << yval[ix] << endl;
        ix++;
    }
}

Ec1 compute_h(const masterkey& mkey, unsigned int sz, const qap& theqap, const string prefix, const wirevalt& wirevals, bool check) {
    // determine roots
    vector<modp> roots(sz);
    modp gen = modp(5)^(modp(-1)/sz);
    roots[0] = modp(1);
    for (unsigned int i = 1; i < sz; i++)
        roots[i] = roots[i-1]*gen;

    // collect randomness from the different blocks
    modp deltav = wirevals.at(prefix+"/deltav");
    modp deltaw = wirevals.at(prefix+"/deltaw");
    modp deltay = wirevals.at(prefix+"/deltay");

    vector<modp> vval(sz), wval(sz), yval(sz);

    computevwyval(theqap.eqs, prefix, wirevals, vval, wval, yval, check);

    // compute vcof, wcof, ycof: coefficients of v,w,y
    std::vector<modp> vcof(sz), wcof(sz), ycof(sz);
    fftinv(roots, vcof, vval); fftinv(roots, wcof, wval); fftinv(roots, ycof, yval);

    // comute vcof2, wcof2, ycof2: coefficients of v,w,y*diag(zeta^0,...,\zeta^{n-1})
    std::vector<modp> vcof2(sz), wcof2(sz), ycof2(sz);
    modp zeta("5"), curfac("1");
    for (unsigned int i = 0; i < sz; i++) {
        vcof2[i] = curfac*vcof[i];
        wcof2[i] = curfac*wcof[i];
        ycof2[i] = curfac*ycof[i];
        curfac=curfac*zeta;
    }
    curfac=curfac-1; // note that curfac is now zeta^(NROOTS)-1: the value of t on {zeta*om, zeta*om^2, ...}

    // compute vvvalb, wvalb, yvalb: values of v,w,y in zeta*om, zeta*om^2, ...; tinv: value of t
    std::vector<modp> vvalb(sz), wvalb(sz), yvalb(sz);
    fft(roots, vvalb, vcof2); fft(roots, wvalb, wcof2); fft(roots, yvalb, ycof2);

    // compute hvalb: value of h in zeta*om, ....
    modp tinv = curfac.inv();

    std::vector<modp> hvalb(sz);
    for (unsigned int i = 0; i < sz; i++)
      hvalb[i]=(vvalb[i]*wvalb[i]-yvalb[i])*tinv;

    // compute inverse fft of hvalb in om, om^2 === inverse of hvalb*diag(...) in zeta*om, ...
    std::vector<modp> hcof(sz);
    fftinv(roots, hcof, hvalb);

    // compute hcofs from inverse fft
    modp zinv = zeta.inv();
    curfac = "1";
    for (unsigned int i = 0; i < sz; i++) {
      hcof[i] = curfac*hcof[i];
      curfac= curfac*zinv;
    }

    modp tmpm=-deltay;
    Ec1 p_h=g1^tmpm;
    modp tmpa=deltav*deltaw;
    p_h=p_h+(mkey.g_s[sz]^tmpa)-(g1^tmpa); // we use here that t(x)=x^sz-1
    for (unsigned int i = 0; i < sz; i++) {
      tmpa=hcof[i]+wcof[i]*deltav+vcof[i]*deltaw;
      p_h=p_h+(mkey.g_s[i]^tmpa);
    }
    return p_h;
}



qapproof qapprove(const masterkey& mkey, const qap& theqap, const qapek& ek, const wirevalt& wirevals, string prefix, bool check) {
    qapproof ret;

    unsigned int sz = 1; while (sz < theqap.eqs.size()) sz<<=1;
    //cerr << "Proving block, sz=" << sz << endl;

//    cerr << "Proving block..." << endl;

    // randomness

    modp deltav = wirevals.at(prefix+"/deltav"),
         deltaw = wirevals.at(prefix+"/deltaw"),
         deltay = wirevals.at(prefix+"/deltay");
//    cerr << "(dv,dw,dy)=(" << deltav << "," << deltaw << "," << deltay << ")" << endl;
    ret.p_rvx  = ek.g_rvt^deltav;
    ret.p_ravx = ek.g_rvavt^deltav;
    ret.p_rwx  = ek.g2_rwt^deltaw;
    ret.p_rawx = ek.g_rwawt^deltaw;
    ret.p_ryx  = ek.g_ryt^deltay;
    ret.p_rayx = ek.g_ryayt^deltay;
    ret.p_z    = (ek.g_rvbt^deltav)+(ek.g_rwbt^deltaw)+(ek.g_rybt^deltay);

    // build vmid, wmid, ymid blocks

    for (auto const& it: ek.wires) {
//        cerr << "Wire " << prefix+"/"+it.first;
        modp val = wirevals.at(prefix+"/"+it.first);
//        cerr << "=" << val << endl;
        ret.p_rvx  += it.second.g_rvvk^val;
        ret.p_ravx += it.second.g_rvavvk^val;
        ret.p_rwx  += it.second.g_rwwk^val;
        ret.p_rawx += it.second.g_rwawwk^val;
        ret.p_ryx  += it.second.g_ryyk^val;
        ret.p_rayx += it.second.g_ryayyk^val;
        ret.p_z    += it.second.g_rvvkrwwkryyk^val;
    }

    for (auto const& it: theqap.blocks) {
        //cerr << "Getting " << prefix+"/rnd2_"+it.first << endl;
        modp rnd = wirevals.at(prefix+"/rnd2_"+it.first);
        //cerr << "Adding randomness " << rnd << endl;
        ret.p_z    += ek.g_beta^rnd;
    }

    // compute "h"

    cerr << "Compute h " << check << endl;


    ret.p_h = compute_h(mkey, sz, theqap, prefix, wirevals, false);

    return ret;
}

