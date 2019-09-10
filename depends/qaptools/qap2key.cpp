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
#include "qap.h"

using namespace std;

void generate_master_skey(mastersk& sk) {
    sk.s = modp::rand();
    sk.rc = modp::rand();
    sk.al = modp::rand();
}

void generate_master_key(const mastersk& sk, unsigned int maxpower, masterkey& mk) {
    Ec1 tmp1;
    Ec2 tmp2;
    modp curfac("1");

    mk.g_al = g2^sk.al;

    mk.g_s = vector<Ec1>(maxpower+1);
    mk.g2_s = vector<Ec2>(maxpower+1);
    mk.g_rcs = vector<Ec1>(maxpower+1);
    mk.g_rcals = vector<Ec2>(maxpower+1);

    for (unsigned int i = 0; i <= maxpower; i++) {
        mk.g_s[i] = g1^curfac;
        mk.g2_s[i] = g2^curfac;
        mk.g_rcs[i] = g1^(curfac*sk.rc);
        mk.g_rcals[i] = g2^(curfac*sk.rc*sk.al);
        curfac = curfac*sk.s;
    }

    //modp tar = curfac-1; // value of the target polynomial in s
    //mk.g_t = g1^tar;
    //mk.g2_t = g2^tar;
}

vector<modp> compute_lagcofs(unsigned int nroots, unsigned int ncofs, const modp& s) {
    modp gen    = modp(5)^(modp(-1)/nroots);
    modp lambda = ((s^nroots)-1)*modp(nroots).inv();
    modp root   = 1;

    vector<modp> ret = vector<modp>();

    for (unsigned int cur = 0; cur < ncofs; cur++) {
        ret.push_back((s-root).inv()*lambda);
        root        = root*gen;
        lambda      = lambda*gen;
    }

    return ret;
}

void generate_coeff_cache(const mastersk& sk, unsigned int nroots, coeffcache& mk) {
    vector<modp> coeffs = compute_lagcofs(nroots, nroots, sk.s);

    mk.g1_coeff = vector<Ec1>(nroots);
    mk.g2_coeff = vector<Ec2>(nroots);

    for (unsigned int i = 0; i < nroots; i++) {
        mk.g1_coeff[i] = g1^coeffs[i];
        mk.g2_coeff[i] = g2^coeffs[i];
    }

}

void generate_coeff_cache(const masterkey& mk, unsigned int nroots, coeffcache& ret) {
    ret.g1_coeff = vector<Ec1>(nroots);
    ret.g2_coeff = vector<Ec2>(nroots);

    // determine roots
    vector<modp> roots(nroots);
    modp gen = modp(5)^(modp(-1)/nroots);
    roots[0] = modp(1);
    for (unsigned int i = 1; i < nroots; i++)
        roots[i] = roots[i-1]*gen;

    vector<modp> vals = vector<modp>(nroots), coefs = vector<modp>(nroots);
    for (unsigned int i = 0; i < nroots; i++) {
        ret.g1_coeff[i] = g10;
        ret.g2_coeff[i] = g20;
        if (i>0) vals[i-1] = 0;
        vals[i] = 1;
        fftinv(roots, coefs, vals); // TODO: speed this up
        for (int j = 0; j < nroots; j++) {
            ret.g1_coeff[i] += mk.g_s[j]^coefs[j]; // TODO: speed this up
            ret.g2_coeff[i] += mk.g2_s[j]^coefs[j];
        }
    }

}

inline bool ispubwire(string wire) {
    return wire == "one" || (wire.c_str()[0] == 'o' && wire.c_str()[1] == '_');
}


void qap2key(const qap& theqap, const masterkey& mk, modp* s, coeffcache* c, qapek& ret1, qapvk& ret2) {
    unsigned int neq = theqap.eqs.size();

    unsigned int qapdeg = 1; while (qapdeg < neq) qapdeg <<= 1;
    cerr << "Using QAP degree=" << qapdeg << endl;

    Ec1 g1tar = mk.g_s[qapdeg]-g1;
    Ec2 g2tar = mk.g2_s[qapdeg]-g2;


    modp alv = modp::rand(),  alw = modp::rand(), aly = modp::rand(),
         rv = modp::rand(),   rw = modp::rand(),  ry = rv*rw,
         rvav = rv*alv,       rwaw = rw*alw,      ryay = ry*aly,
         beta = modp::rand(),
         rvb = rv*beta,       rwb = rw*beta,      ryb = ry*beta;

    ret1.g_rvt   = g1tar^rv;
    ret1.g_rvavt = g2tar^rvav;
    ret1.g2_rwt  = g2tar^rw;
    ret1.g_rwawt = g1tar^rwaw;
    ret1.g_ryt   = g1tar^ry;
    ret1.g_ryayt = g2tar^ryay;
    ret1.g_beta  = g1^beta;
    ret1.g_rvbt  = g1tar^rvb;
    ret1.g_rwbt  = g1tar^rwb;
    ret1.g_rybt  = g1tar^ryb;

    ret2.g2alv   = g2^alv;
    ret2.g1alw   = g1^alw;
    ret2.g2aly   = g2^aly;
    ret2.g2ryt   = g2tar^ry;
    ret2.g1bet   = g1^beta;
    ret2.g2bet   = g2^beta;

    if (s != NULL) { // using master secret key
        map<string,modp> vis = map<string,modp>();
        map<string,modp> wis = map<string,modp>();
        map<string,modp> yis = map<string,modp>();

        vector<modp> lagcofs = compute_lagcofs(qapdeg, neq, *s);

        int cur = 0;
        for (auto const& eq: theqap.eqs) {
            modp lagcof = lagcofs[cur++];
            for (auto const& vcur: eq.v) {
                vis[vcur.te] = vis[vcur.te]+lagcof*vcur.co;
            }
            for (auto const& wcur: eq.w) {
                wis[wcur.te] = wis[wcur.te]+lagcof*wcur.co;
            }
            for (auto const& ycur: eq.y) {
                yis[ycur.te] = yis[ycur.te]+lagcof*ycur.co;
            }               
            //interpolate(lagcofs[cur++], eq, vis, wis, yis);
        }
        
        // generate evaluation keys for all values
        // TODO: this does not always work since vis.end() == wis.end() == yis.end() for empty lists???
        unordered_set<string> done = unordered_set<string>();
        for (map<string,modp>::iterator iter = vis.begin(); iter != yis.end(); ) {
            if (iter == vis.end()) { iter = wis.begin(); continue; }
            if (iter == wis.end()) { iter = yis.begin(); continue; }

            if (done.find(iter->first) == done.end()) {
                done.insert(iter->first);

                modp& vval = vis[iter->first], wval = wis[iter->first], yval = yis[iter->first];

                if (ispubwire(iter->first)) {
                    wirevk wvk;
                    wvk.g_rvvk = g1^(rv*vval);
                    wvk.g_rwwk = g2^(rw*wval);
                    wvk.g_ryyk = g1^(ry*yval);
                    ret2.pubinputs[iter->first] = wvk;
                } else {
                    wireek ek;
                    ek.g_rvvk   = g1^(rv*vval);
                    ek.g_rwwk   = g2^(rw*wval);
                    ek.g_ryyk   = g1^(ry*yval);
                    ek.g_rvavvk = g2^(rvav*vval);
                    ek.g_rwawwk = g1^(rwaw*wval);
                    ek.g_ryayyk = g2^(ryay*yval);
                    ek.g_rvvkrwwkryyk = g1^((rv*vval+rw*wval+ry*yval)*beta);
                    ret1.wires[iter->first] = ek;
                }
            }

            iter++;
        }
    } else { // using coefficient cache
        // initialise pubinputs and wires
        unordered_set<string> wires = unordered_set<string>();
        for (auto const& eq: theqap.eqs) {
            for (auto const& term: eq.v) wires.insert(term.te);
            for (auto const& term: eq.w) wires.insert(term.te);
            for (auto const& term: eq.y) wires.insert(term.te);
        }
        
        for (auto const& wire: wires) {
            if (ispubwire(wire)) {
                wirevk wvk;
                wvk.g_rvvk = g10;
                wvk.g_rwwk = g20;
                wvk.g_ryyk = g10;
                ret2.pubinputs[wire] = wvk;
            } else {
                wireek ek;
                ek.g_rvvk   = g10;
                ek.g_rwwk   = g20;
                ek.g_ryyk   = g10;
                ek.g_rvavvk = g20;
                ek.g_rwawwk = g10;
                ek.g_ryayyk = g20;
                ek.g_rvvkrwwkryyk = g10;
                ret1.wires[wire] = ek;                        
            }
        }
        
        int cur = 0;
        for (auto const& eq: theqap.eqs) {
            for (auto const& vcur: eq.v) {
                if (ispubwire(vcur.te)) {
                    ret2.pubinputs[vcur.te].g_rvvk     += c->g1_coeff[cur]^(rv*vcur.co);
                } else {
                    ret1.wires[vcur.te].g_rvvk         += c->g1_coeff[cur]^(rv*vcur.co);
                    ret1.wires[vcur.te].g_rvavvk       += c->g2_coeff[cur]^(rvav*vcur.co);
                    ret1.wires[vcur.te].g_rvvkrwwkryyk += c->g1_coeff[cur]^(rv*beta*vcur.co);                 
                }
            }
            for (auto const& wcur: eq.w) {
                if (ispubwire(wcur.te)) {
                    ret2.pubinputs[wcur.te].g_rwwk     += c->g2_coeff[cur]^(rw*wcur.co);
                } else {
                    ret1.wires[wcur.te].g_rwwk         += c->g2_coeff[cur]^(rw*wcur.co);
                    ret1.wires[wcur.te].g_rwawwk       += c->g1_coeff[cur]^(rwaw*wcur.co);
                    ret1.wires[wcur.te].g_rvvkrwwkryyk += c->g1_coeff[cur]^(rw*beta*wcur.co);                 
                }
            }
            for (auto const& ycur: eq.y) {
                if (ispubwire(ycur.te)) {
                    ret2.pubinputs[ycur.te].g_ryyk     += c->g1_coeff[cur]^(ry*ycur.co);
                } else {
                    ret1.wires[ycur.te].g_ryyk         += c->g1_coeff[cur]^(ry*ycur.co);
                    ret1.wires[ycur.te].g_ryayyk       += c->g2_coeff[cur]^(ryay*ycur.co);
                    ret1.wires[ycur.te].g_rvvkrwwkryyk += c->g1_coeff[cur]^(ry*beta*ycur.co);                 
                }
            }
            cur++;
        }
    }
        
    // generate keys for all block types

    int totix = 1; // current index in overall beta block

    for (auto const& blk: theqap.blocks) {
//        cerr << "Generating block " << blk.first << ", start=" << totix << endl;
        unsigned int sz = blk.second.size();
        modp cural = modp::rand(), curbet = modp::rand();

        blockek ek;
        ek.gstart = totix;
        ek.g2als = vector<Ec2>(sz);
        ek.g1betas = vector<Ec1>(sz);
        ek.g2al = g2^cural;
        ek.g1betar1 = mk.g_rcs[0]^curbet;
        ek.g1betar2 = g1^curbet;
        for (unsigned int i = 0; i < sz; i++) {
            ek.g2als[i] = mk.g2_s[totix]^cural;
            ek.g1betas[i] = (mk.g_s[totix]+mk.g_rcs[i+1])^curbet;
            ret1.wires[blk.second[i]].g_rvvkrwwkryyk += mk.g_s[totix]^beta;
            totix++;
        }
        ret1.blocks[blk.first] = ek;

        blockvk vk;
        vk.g2al = g2^cural;
        vk.g2beta = g2^curbet;
        ret2.blocks[blk.first] = vk;
    }
}
