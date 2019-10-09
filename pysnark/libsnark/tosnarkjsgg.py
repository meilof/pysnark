vkin = open("pysnark_vk", "r")
vkout = open("verification_key.json", "w")

print('{', file=vkout)
print(' "protocol": "groth",', file=vkout)

def process_g2(nm, fin, fout, skipcomma=False):
    a1=list(map(lambda x:x.strip(),next(fin).split(" ")))
    a2=list(map(lambda x:x.strip(),next(fin).split(" ")))
    print(' "' + nm + '": [', file=fout)
    print('   [ "' + a1[0] + '", "' + a1[1] + '"],', file=fout)
    print('   [ "' + a2[0] + '", "' + a2[1] + '"],', file=fout)
    print('   [ "1", "0" ] ]' + ('' if skipcomma else ','), file=fout)

def process_g1(nm, fin, fout):
    b=[next(fin).strip(), next(fin).strip()]
    print(' "' + nm + '": ["' + b[0] + '", "' + b[1] + '", "1" ],', file=fout)
    
f12=list(map(lambda x:x.strip(),next(vkin).split(" ")))
print(' "vk_alfabeta_12": [', file=vkout)
print('   [', file=vkout)
print('    ["' + f12[0] + '", "' + f12[1] + '"],', file=vkout)
print('    ["' + f12[2] + '", "' + f12[3] + '"],', file=vkout)
print('    ["' + f12[4] + '", "' + f12[5] + '"]', file=vkout)
print('   ], [', file=vkout)
print('    ["' + f12[6] + '", "' + f12[7] + '"],', file=vkout)
print('    ["' + f12[8] + '", "' + f12[9] + '"],', file=vkout)
print('    ["' + f12[10] + '", "' + f12[11] + '"]', file=vkout)
print('   ]', file=vkout)
print('  ],', file=vkout)

process_g2("vk_gamma_2", vkin, vkout)
process_g2("vk_delta_2", vkin, vkout)

nin = int(next(vkin).strip())
print(' "nPublic": ' + str(nin-1) + ',', file=vkout)

print(' "IC": [', file=vkout)
for i in range(nin):
    b=[next(vkin).strip(), next(vkin).strip()]
    print('  ["' + b[0] + '", "' + b[1] + '", "1"]' + (',' if i!=nin-1 else ''), file=vkout)
print(' ],', file=vkout)

process_g1("vk_alfa_1", vkin, vkout)
process_g2("vk_beta_2", vkin, vkout, True)

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
process_g2("pi_b", login, proofout)
process_g1("pi_c", login, proofout)
print(' "protocol": "groth"', file=proofout)
print('}', file=proofout)

print('*** Created proof.json, verification_key.json, public.json; test using "snarkjs verify"')