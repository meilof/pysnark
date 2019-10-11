%inline %{
    
template<typename ppT>
void prettywrite(std::ostream &out, const r1cs_ppzksnark_verification_key<ppT> &vk) {
    prettywrite(out, vk.alphaA_g2);
    prettywrite(out, vk.alphaB_g1);
    prettywrite(out, vk.alphaC_g2);
    prettywrite(out, vk.gamma_g2);
    prettywrite(out, vk.gamma_beta_g1);
    prettywrite(out, vk.gamma_beta_g2);
    prettywrite(out, vk.rC_Z_g2);
    prettywrite(out, vk.encoded_IC_query);    
}
    
libsnark::r1cs_ppzksnark_keypair<libsnark::default_r1cs_ppzksnark_pp>* zk_read_key(const char* ekfile, const libsnark::r1cs_constraint_system<Ft>* cs = NULL) {
    // try reading from file
    
    ifstream ek_data(ekfile);
    if (!ek_data.is_open()) return NULL;

    int sz1;
    ek_data >> sz1;
    
    // initial check to eliminate obvious non-matches
    if (cs!=NULL && (sz1!=cs->constraints.size())) return NULL;
        
    libsnark::r1cs_ppzksnark_keypair<libsnark::default_r1cs_ppzksnark_pp>* keys = 
        new libsnark::r1cs_ppzksnark_keypair<libsnark::default_r1cs_ppzksnark_pp>();
    
    ek_data >> keys->pk;
    ek_data >> keys->vk;
    ek_data.close();
    
    if (cs!=NULL && !cseq(keys->pk.constraint_system, *cs)) {
        delete keys;
        return NULL;
    }
    
    return keys;
}
    
void zk_write_keys(const libsnark::r1cs_ppzksnark_keypair<libsnark::default_r1cs_ppzksnark_pp>& keypair,
            const char* vkfile = NULL, const char* ekfile = NULL) {
    if (vkfile && *vkfile) {
        ofstream vk_data(vkfile);
        prettywrite(vk_data, keypair.vk);
        //vk_data << keypair.vk;
        vk_data.close();
    }
    
    if (ekfile && *ekfile) {
        ofstream ek_data(ekfile);
        ek_data << keypair.pk.constraint_system.constraints.size() << endl;
        ek_data << keypair.pk;
        ek_data << keypair.vk;
        ek_data.close();    
    }
}
    
void zk_write_proof(
    const libsnark::r1cs_ppzksnark_proof<libsnark::default_r1cs_ppzksnark_pp>& proof,
    const libsnark::r1cs_primary_input<Ft> pubvals,
    const char* logfile
) {
    ofstream prooffile(logfile);

    prooffile << pubvals.size() << endl;
    for (auto &it: pubvals) { prettywrite(prooffile, it); prooffile << endl; }

    prettywrite(prooffile, proof.g_A.g);
    prettywrite(prooffile, proof.g_A.h);
    prettywrite(prooffile, proof.g_B.g);
    prettywrite(prooffile, proof.g_B.h);
    prettywrite(prooffile, proof.g_C.g);
    prettywrite(prooffile, proof.g_C.h);
    prettywrite(prooffile, proof.g_H);
    prettywrite(prooffile, proof.g_K);

    prooffile.close();
}


%}
