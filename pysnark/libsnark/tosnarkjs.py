vkin = open("pysnark_vk", "r")
vkout = open("verification_key.json", "w")

print('{', file=vkout)
print(' "protocol": "original",', file=vkout)

def process_g2(nm, fin, fout):
    a1=list(map(lambda x:x.strip(),next(fin).split(" ")))
    a2=list(map(lambda x:x.strip(),next(fin).split(" ")))
    print(' "' + nm + '": [', file=fout)
    print('   [ "' + a1[0] + '", "' + a1[1] + '"],', file=fout)
    print('   [ "' + a2[0] + '", "' + a2[1] + '"],', file=fout)
    print('   [ "1", "0" ] ],', file=fout)

def process_g1(nm, fin, fout):
    b=[next(fin).strip(), next(fin).strip()]
    print(' "' + nm + '": ["' + b[0] + '", "' + b[1] + '", "1" ],', file=fout)

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
    b=[next(vkin).strip(), next(vkin).strip()]
    print('  ["' + b[0] + '", "' + b[1] + '", "1"]' + (',' if i!=nin-1 else ''), file=vkout)
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
