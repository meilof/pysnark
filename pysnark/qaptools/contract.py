# Copyright (c) 2016-2018 Koninklijke Philips N.V. All rights reserved. A
# copyright license for redistribution and use in source and binary forms,
# with or without modification, is hereby granted for non-commercial,
# experimental and research purposes, provided that the following conditions
# are met:
# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimers.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimers in the
#   documentation and/or other materials provided with the distribution. If
#   you wish to use this software commercially, kindly contact
#   info.licensing@philips.com to obtain a commercial license.
#
# This license extends only to copyright and does not include or grant any
# patent license or other license whatsoever.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import glob
import os
import os.path
import shutil
import subprocess
import sys

from . import options

def tog1(tok):  return [0, 0] if tok == "0" else [int(x, 0) for x in tok.split("_")]
def tog2(tok):  return [0, 0, 0, 0] if tok == "0" else [int(x, 0) for x in tok[1:-1].replace("]_[", ",").split(",")]
def readg1(fl): return tog1(fl.readline().strip())
def readg2(fl): return tog2(fl.readline().strip())
def strg1(val): return "Pairing.G1Point(" + str(val[0]) + "," + str(val[1]) + ")"
def strg2(val): return "Pairing.G2Point([" + str(val[1]) + "," + str(val[0]) + "],[" + str(val[3]) + "," + str(val[2]) + "])"
def strg1p(ix): return "Pairing.G1Point(proof[%d],proof[%d])" % (ix, ix + 1)
def strg2p(ix): return "Pairing.G2Point([proof[%d],proof[%d]],[proof[%d],proof[%d]])" % (ix + 1, ix, ix + 3, ix + 2)

class QapVk:
    def __init__(self, fn):
        qapvk = open(fn)
        qapvk.readline()
        [self.g2alv, self.g1alw, self.g2aly, self.g2ryt, self.g1bet, self.g2bet] =\
              [readg2(qapvk), readg1(qapvk), readg2(qapvk),
               readg2(qapvk), readg1(qapvk), readg2(qapvk)]
        self.blocks = dict()
        ln = qapvk.readline().strip()
        while ln != ".":
            toks = ln.split(" ")
            self.blocks[toks[0]] = (tog2(toks[2]), tog2(toks[3]))
            ln = qapvk.readline().strip()
        self.pubinputs = dict()
        ln = qapvk.readline().strip()
        while ln != "]":
            toks = ln.split(" ")
            self.pubinputs[toks[0]] = (tog1(toks[2]), tog2(toks[3]), tog1(toks[4]))
            ln = qapvk.readline().strip()

def contract():
    print("** Building contract")
    contractdir = options.get_contract_dir()
    conttestdir = options.get_conttest_dir()

    if not os.path.isdir(contractdir):
        print("*** Contract directory \"" + contractdir + "\" does not exist; run \"truffle init\" or create the directory first", file=sys.stderr)
        sys.exit(2)

    if not os.path.isdir(conttestdir):
        print("*** Contract test directory \"" + conttestdir + "\" does not exist; run \"truffle init\" or create the directory first", file=sys.stderr)
        sys.exit(2)

    #prove.prove()

    # copy all predefined contracts to the contract dir
    try:
        patt = os.path.join(os.path.abspath(os.path.dirname(__file__)), '*.sol')
        for fl in glob.glob(patt):
            print("Import Solidity script", fl, file=sys.stderr)
            shutil.copyfile(fl, os.path.join(contractdir, os.path.basename(fl)))
    except NameError:
        # this seems to occur when calling pysnark/contract.py directly
        pass

    contract = open(os.path.join(contractdir, "Pysnark.sol"), "w")

    print("""\
pragma solidity ^0.5.0;

import "truffle/Assert.sol";
import "../contracts/Pairing.sol";

contract Pysnark {
	event Verified(string);
	function verify(uint[] memory proof, uint[] memory io) public returns (bool r) {
	    Pairing.G1Point memory p_rvx;
	    Pairing.G1Point memory p_ryx;
	    Pairing.G1Point memory versum;
	    Pairing.G2Point memory p_rwx;
""", file=contract)

    prooff = open(options.get_proof_file())
    proof = []
    ios = []

    iovals = dict()
    for ln in open(options.get_io_file()):
        ln = ln.strip()
        if ln=="" or ln[0]=="#": continue
        nm, val = ln.split(" ")
        iovals[nm[:-1]] = int(val)
    print("iovals", iovals)

    def proofg1(tok):
        vals = tog1(tok)
        ix = len(proof)
        proof.extend(vals)
        return ix

    def proofg1r():
        return proofg1(prooff.readline().strip())

    def proofg2(tok):
        vals = tog2(tok)
        ix = len(proof)
        proof.extend(vals)
        return ix

    def proofg2r():
        return proofg2(prooff.readline().strip())

    # read master key
    mkeyfile = open(options.get_mpkey_file())
    mkeyfile.readline()
    g_al = readg2(mkeyfile)
    mkeyfile.close()

    qapvks = dict()
    qap2vk = dict()
    pblocks = dict()

    for ln in open(options.get_schedule_file()):
        toks = ln.strip().split(" ")
        if toks[0] == "[function]":
            curfname = toks[1]

            print("        // [function]", curfname, file=contract)

            # read proof
            ln = prooff.readline().strip()
            if ln != "geppetri_qapproof [":
                raise ValueError("*** Malformed proof: expected proof block, got something else")

            # verification key
            if not toks[4] in qapvks: qapvks[toks[4]] = QapVk(toks[4])
            qap2vk[curfname] = toks[4]
            qv = qapvks[toks[4]]

            # proof
            p_rvx,p_rwx,p_ryx,p_ravx,p_rawx,p_rayx,p_z,p_h = [proofg1r(), proofg2r(), proofg1r(), proofg2r(), proofg1r(), proofg2r(), proofg1r(), proofg1r()]
            ln=prooff.readline().strip()
            while ln!="]":
                toks = ln.split(" ")
                pblocks[curfname+"/"+toks[0]] = (proofg1(toks[2]), proofg2(toks[3]), proofg1(toks[4]))
                ln = prooff.readline().strip()

            # opt_atePairing(e1, proof.p_ravx, g1);
            # opt_atePairing(e2, qvk.g2alv, proof.p_rvx);
            # if (e1 != e2) {cerr << "*** p_ravx pairing check failed" << endl;}
            print("        p_rvx = %s;" % (strg1p(p_rvx)), file=contract)
            print("        if (!Pairing.pairingProd2(Pairing.P1(), %s, Pairing.negate(%s), %s)) return false;" % (strg2p(p_ravx), "p_rvx", strg2(qv.g2alv)), file=contract)

            # opt_atePairing(e1, g2, proof.p_rawx);
            # opt_atePairing(e2, proof.p_rwx, qvk.g1alw);
            # if (e1 != e2) {cerr << "*** p_rawx pairing check failed" << endl;}
            print("        p_rwx = %s;" % (strg2p(p_rwx)), file=contract)
            print("        if (!Pairing.pairingProd2(%s, Pairing.P2(), Pairing.negate(%s), %s)) return false;" % (strg1p(p_rawx), strg1(qv.g1alw), "p_rwx"), file=contract)

            # opt_atePairing(e1, proof.p_rayx, g1);
            # opt_atePairing(e2, qvk.g2aly, proof.p_ryx);
            # if (e1 != e2) {cerr << "*** p_rayx pairing check failed" << endl;}
            print("        p_ryx = %s;" % (strg1p(p_ryx)), file=contract)
            print("        if (!Pairing.pairingProd2(Pairing.P1(), %s, Pairing.negate(%s), %s)) return false;" % (strg2p(p_rayx), "p_ryx", strg2(qv.g2aly)), file=contract)


            # Ec1 versum = proof.p_rvx + proof.p_ryx;
            print("        versum = Pairing.doadd(p_rvx, p_ryx);", file=contract)

            # for (auto const & it: proof.blocks) versum += it.second.comm;
            for b in qv.blocks:
                print("        versum = Pairing.doadd(versum, %s);" % (strg1p(pblocks[curfname+"/"+b][0])), file=contract)

            # opt_atePairing(e1, g2, proof.p_z);
            # opt_atePairing(e2, qvk.g2bet, versum);
            # opt_atePairing(e3, proof.p_rwx, qvk.g1bet);
            print("        if (!Pairing.pairingProd3(versum, %s, %s, %s, Pairing.negate(%s), Pairing.P2())) return false;" % (strg2(qv.g2bet), strg1(qv.g1bet), strg2p(p_rwx), strg1p(p_z)), file=contract)

            # Ec1 pub_rvx = g10;
            # Ec2 pub_rwx = g20;
            # Ec1 pub_ryx = g10;
            # for (auto const & it: qvk.pubinputs) {
            #     modp val = it.first == "one" ? 1: pubwires.at(prefix + "/" + it.first);
            # //  cerr << "including " << it.first << "=" << val << endl;
            # pub_rvx += it.second.g_rvvk ^ val;
            # pub_rwx += it.second.g_rwwk ^ val;
            # pub_ryx += it.second.g_ryyk ^ val;
            # }
            for it in sorted(qv.pubinputs.keys()):
                gs = qv.pubinputs[it]

                if gs[0]!=[0,0]:
                    val = strg1(gs[0]) if it=="one" else "Pairing.domul(%s, io[%d])" % (strg1(gs[0]), len(ios))
                    print("        p_rvx = Pairing.doadd(p_rvx, %s);" % val, file=contract)

                if gs[1]!=[0,0,0,0]:
                    val = strg2(gs[1]) if it=="one" else "Pairing.domul(%s, io[%d])" % (strg2(gs[1]), len(ios))
                    print("        p_rwx = Pairing.doadd(p_rwx, %s);" % val, file=contract)

                if gs[2]!=[0,0]:
                    val = strg1(gs[2]) if it=="one" else "Pairing.domul(%s, io[%d])" % (strg1(gs[2]), len(ios))
                    print("        p_ryx = Pairing.doadd(p_ryx, %s);" % val, file=contract)

                if it!="one":
                    ios.append((curfname + "/" + it,iovals[curfname + "/" + it]))

            # opt_atePairing(e1, pub_rwx + proof.p_rwx, pub_rvx + proof.p_rvx);
            # opt_atePairing(e2, qvk.g2ryt, proof.p_h);
            # opt_atePairing(e3, g2, pub_ryx + proof.p_ryx);
            # if (e1 != (e2 * e3)) {cerr << "*** divisibility check failed" << endl;}
            print("        if (!Pairing.pairingProd3(%s, %s, %s, Pairing.P2(), Pairing.negate(%s), %s)) return false;" % \
                              (strg1p(p_h), strg2(qv.g2ryt), "p_ryx", "p_rvx", "p_rwx"), file=contract)
        elif toks[0] == "[external]":
            fun = toks[1]
            blk = toks[2]
            blkfile = toks[3]

            print("        // checking external block", blk, file=contract)

            qv = qapvks[qap2vk[fun]]

            # read block file
            _,_,g1s,g2s,_ = open(toks[4]).read().strip().split(" ")
            dbcomm = tog1(g1s)
            dbcommal = tog2(g2s)

            #     opt_atePairing(e1, mk.g_al, db.comm);
            #     opt_atePairing(e2, db.commal, g1);
            #     if (e1 != e2) {cerr << "*** c-alpha pairing check failed" << endl;}
            print("        if (!Pairing.pairingProd2(Pairing.P1(), %s, Pairing.negate(%s), %s)) return false;" % \
                              (strg2(dbcommal), strg1(dbcomm), strg2(g_al)), file=contract)

            # opt_atePairing(e1, bvk.g2al, block.comm);
            # opt_atePairing(e2, block.commal, g1);
            # if (e1 != e2) {cerr << "*** c'-alpha pairing check failed" << endl;}
            print("        if (!Pairing.pairingProd2(Pairing.P1(), %s, Pairing.negate(%s), %s)) return false;" % \
                              (strg2p(pblocks[fun+"/"+blk][1]), strg1p(pblocks[fun+"/"+blk][0]), strg2(qv.blocks[blk][0])), file=contract)

            # opt_atePairing(e1, bvk.g2beta, db.comm + block.comm);
            # opt_atePairing(e2, g2, block.commz);
            # if (e1 != e2) {cerr << "*** block z pairing check failed" << endl;}
            print("        if (!Pairing.pairingProd2(%s, Pairing.P2(), Pairing.negate(Pairing.doadd(%s,%s)), %s)) return false;" % \
                              (strg1p(pblocks[fun+"/"+blk][2]), strg1p(pblocks[fun+"/"+blk][0]), strg1(dbcomm), strg2(qv.blocks[blk][1])), file=contract)

        elif toks[0] == "[glue]":
            fun1 = toks[1]
            qv1 = qapvks[qap2vk[toks[1]]]
            blk1 = toks[2]
            fun2 = toks[3]
            qv2 = qapvks[qap2vk[toks[3]]]
            blk2 = toks[4]

            print("        // checking glue", toks[1], toks[2], toks[3], toks[4], file=contract)

            # read block file
            _,_,g1s,g2s,_ = prooff.readline().strip().split(" ")
            dbcomm = tog1(g1s)
            dbcommal = tog2(g2s)

            #     opt_atePairing(e1, mk.g_al, db.comm);
            #     opt_atePairing(e2, db.commal, g1);
            #     if (e1 != e2) {cerr << "*** c-alpha pairing check failed" << endl;}
            print("        if (!Pairing.pairingProd2(Pairing.P1(), %s, Pairing.negate(%s), %s)) return false;" % \
                              (strg2(dbcommal), strg1(dbcomm), strg2(g_al)), file=contract)

            # opt_atePairing(e1, bvk.g2al, block.comm);
            # opt_atePairing(e2, block.commal, g1);
            # if (e1 != e2) {cerr << "*** c'-alpha pairing check failed" << endl;}
            print("        if (!Pairing.pairingProd2(Pairing.P1(), %s, Pairing.negate(%s), %s)) return false;" % \
                              (strg2p(pblocks[fun1+"/"+blk1][1]), strg1p(pblocks[fun1+"/"+blk1][0]), strg2(qv1.blocks[blk1][0])), file=contract)

            # opt_atePairing(e1, bvk.g2beta, db.comm + block.comm);
            # opt_atePairing(e2, g2, block.commz);
            # if (e1 != e2) {cerr << "*** block z pairing check failed" << endl;}
            print("        if (!Pairing.pairingProd2(%s, Pairing.P2(), Pairing.negate(Pairing.doadd(%s,%s)), %s)) return false;" % \
                              (strg1p(pblocks[fun1+"/"+blk1][2]), strg1p(pblocks[fun1+"/"+blk1][0]), strg1(dbcomm), strg2(qv1.blocks[blk1][1])), file=contract)

            # opt_atePairing(e1, bvk.g2al, block.comm);
            # opt_atePairing(e2, block.commal, g1);
            # if (e1 != e2) {cerr << "*** c'-alpha pairing check failed" << endl;}
            print("        if (!Pairing.pairingProd2(Pairing.P1(), %s, Pairing.negate(%s), %s)) return false;" % \
                              (strg2p(pblocks[fun2+"/"+blk2][1]), strg1p(pblocks[fun2+"/"+blk2][0]), strg2(qv2.blocks[blk2][0])), file=contract)

            # opt_atePairing(e1, bvk.g2beta, db.comm + block.comm);
            # opt_atePairing(e2, g2, block.commz);
            # if (e1 != e2) {cerr << "*** block z pairing check failed" << endl;}
            print("        if (!Pairing.pairingProd2(%s, Pairing.P2(), Pairing.negate(Pairing.doadd(%s,%s)), %s)) return false;" % \
                              (strg1p(pblocks[fun2+"/"+blk2][2]), strg1p(pblocks[fun2+"/"+blk2][0]), strg1(dbcomm), strg2(qv2.blocks[blk2][1])), file=contract)



        # Pairing.G1Point memory g0 = Pairing.P1();
        # Pairing.G1Point memory rvx;
        # rvx.X = 12515936394183002243271507260196859297697047505961740101294664765909221898723;
        # rvx.Y = 14039942389191639593154592279286242158242020084903989822228213123482761997702;
        # Pairing.G2Point memory ravx;
        # ravx.X[1] = 2695248548659602739433667171596926269054529700196716495841421091337757394529;
        # ravx.X[0] = 3387350190847733571771957296457018043949190490077623580281959116333189800007;
        # ravx.Y[1] = 14691563768395631166455534331654963718268108664622736467511112550281775684520;
        # ravx.Y[0] = 14831779390898888209554491569204109776090829532124763641167529752805161346011;
        # Pairing.G2Point memory g2alv;
        # g2alv.X[1] = 5246835310509257254858642984295810516584817371592992387764061488788476496032;
        # g2alv.X[0] = 21440173107593148482816683042123880676180780996229737904399176241517645721350;
        # g2alv.Y[1] = 20410128128429030092444565389491254378650848811039843094043832338265343251897;
        # g2alv.Y[0] = 2639225043932804836026170716721875591615899493131072898408613463598634158790;
        # if (!Pairing.pairingProd2(rvx, g2alv, Pairing.negate(g0), ravx)) return false;

    print("""\
        return true;
    }
}       
    """, file=contract)

    conttest = open(os.path.join(conttestdir, "TestPysnark.sol"), "w")

    print("""\
pragma solidity ^0.5.0;

import "truffle/Assert.sol";
import "../contracts/Pysnark.sol";

contract TestPysnark {
    function testVerifies() public {
        Pysnark ps = new Pysnark();
        uint[] memory proof = new uint[](%d);
        uint[] memory io = new uint[](%d);\
""" % (len(proof), len(ios)), file=conttest)
    for (ix, val) in enumerate(proof):
        print("        proof[%d] = %d;" % (ix,val), file=conttest)
    for (ix, (nm,val)) in enumerate(ios):
        print("        io[%d] = %d; // %s" % (ix,val,nm), file=conttest)

    print("""\
        Assert.equal(ps.verify(proof, io), true, "Proof should verify");
    }
}
""", file=conttest)

if __name__ == "__main__":
    contract()
else:
    if 'sphinx' not in sys.modules and options.do_pysnark() and options.do_proof():
        import atexit
        print("** Registring")
        atexit.register(maybe(contract))
        import prove
