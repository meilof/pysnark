import json
import libsnark.alt_bn128 as libsnark

class SnarkjsEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, libsnark.G1):
            return [str(obj.getx()), str(obj.gety()), str(obj.getz())]
        if isinstance(obj, libsnark.G2):
            return [self.default(obj.X), self.default(obj.Y), self.default(obj.Z)]
        if isinstance(obj, libsnark.Fq2t):
            return [str(obj.getc0()), str(obj.getc1())]
        if isinstance(obj, libsnark.ZKVerificationKey):
            return {"protocol":"original",
                    "vk_a":    self.default(obj.alphaA_g2),
                    "vk_b":    self.default(obj.alphaB_g1),
                    "vk_c":    self.default(obj.alphaC_g2),
                    "vk_g":    self.default(obj.gamma_g2),
                    "vk_gb_1": self.default(obj.gamma_beta_g1),
                    "vk_gb_2": self.default(obj.gamma_beta_g2),
                    "vk_z":    self.default(obj.rC_Z_g2),
                    "nPublic": obj.encoded_IC_query_size()-1,
                    "IC":      [self.default(obj.encoded_IC_query(i)) for i in range(obj.encoded_IC_query_size())]
                   }
        if isinstance(obj, libsnark.R1csPrimaryInput):
            return [str(obj.at(i)) for i in range(obj.size())]
        if isinstance(obj, libsnark.ZKProof):
            return {"protocol": "original",
                    "pi_a": self.default(obj.g_A.g),
                    "pi_ap": self.default(obj.g_A.h),
                    "pi_b": self.default(obj.g_B.g),
                    "pi_bp": self.default(obj.g_B.h),
                    "pi_c": self.default(obj.g_C.g),
                    "pi_cp": self.default(obj.g_C.h),
                    "pi_h": self.default(obj.g_H),
                    "pi_kp": self.default(obj.g_K)
                   }
        return json.JSONEncoder.default(self, obj)
    
if __name__ == "__main__":
    vkin = open("pysnark_vk", "r")
    vkout = open("verification_key.json", "w")

    print('{', file=vkout)
    print(' "protocol": "original",', file=vkout)

    def process_g2(nm, fin, fout):
        a1=list(map(lambda x:x.strip(),next(fin).split(" ")))
        a2=list(map(lambda x:x.strip(),next(fin).split(" ")))
        a3=list(map(lambda x:x.strip(),next(fin).split(" ")))
        print(' "' + nm + '": [', file=fout)
        print('   [ "' + a1[0] + '", "' + a1[1] + '"],', file=fout)
        print('   [ "' + a2[0] + '", "' + a2[1] + '"],', file=fout)
        print('   [ "' + a3[0] + '", "' + a3[1] + '"]', file=fout)
        print('  ],', file=fout)

    def process_g1(nm, fin, fout):
        b=[next(fin).strip(), next(fin).strip(), next(fin).strip()]
        print(' "' + nm + '": ["' + b[0] + '", "' + b[1] + '", "' + b[2] + '" ],', file=fout)

    process_g2("vk_a", vkin, vkout)
    process_g1("vk_b", vkin, vkout)
    process_g2("vk_c", vkin, vkout)
    process_g2("vk_g", vkin, vkout)
    process_g1("vk_gb_1", vkin, vkout)
    process_g2("vk_gb_2", vkin, vkout)
    process_g2("vk_z", vkin, vkout)

    nin = int(next(vkin).strip())
    print(' "nPublic": ' + str(nin-1) + ',', file=vkout)

    print(' "IC": [', file=vkout)
    for i in range(nin):
        b=[next(vkin).strip(), next(vkin).strip(), next(vkin).strip()]
        print('  ["' + b[0] + '", "' + b[1] + '", "' + b[2] + '"]' + (',' if i!=nin-1 else ''), file=vkout)
    print(' ]', file=vkout)
    print('}', file=vkout)

    login = open("pysnark_log", "r")
    pubout = open("public.json", "w")
    proofout = open("proof.json", "w")

    npub = int(next(login).strip())

    print('[', file=pubout)
    for i in range(npub):
        print('  "' + next(login).strip() + '"' + (',' if i!=npub-1 else ''), file=pubout)
    print(']', file=pubout)

    print('{', file=proofout)
    process_g1("pi_a", login, proofout)
    process_g1("pi_ap", login, proofout)
    process_g2("pi_b", login, proofout)
    process_g1("pi_bp", login, proofout)
    process_g1("pi_c", login, proofout)
    process_g1("pi_cp", login, proofout)
    process_g1("pi_h", login, proofout)
    process_g1("pi_kp", login, proofout)
    print(' "protocol": "original"', file=proofout)
    print('}', file=proofout)

    print('*** Created proof.json, verification_key.json, public.json; test using "snarkjs verify"')