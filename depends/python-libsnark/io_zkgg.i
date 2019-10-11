%inline %{
    
template<mp_size_t n, const bigint<n>& modulus>
void prettywrite(std::ostream &out, const Fp6_3over2_model<n, modulus> &el)
{
    prettywrite(out, el.c0); out << " ";
    prettywrite(out, el.c1); out << " ";
    prettywrite(out, el.c2);
}
    
template<mp_size_t n, const bigint<n>& modulus>
void prettywrite(std::ostream &out, const Fp12_2over3over2_model<n, modulus> &el)
{
    prettywrite(out, el.c0); out << " ";
    prettywrite(out, el.c1); out << endl;
}    
    
template<typename ppT>
void prettywrite(std::ostream &out, const r1cs_gg_ppzksnark_verification_key<ppT> &vk) {
    prettywrite(out, vk.alpha_g1_beta_g2);
    prettywrite(out, vk.gamma_g2);
    prettywrite(out, vk.delta_g2);
    prettywrite(out, vk.gamma_ABC_g1);
}
    
libsnark::r1cs_gg_ppzksnark_keypair<libsnark::default_r1cs_gg_ppzksnark_pp>* zkgg_read_key(const char* ekfile, const libsnark::r1cs_constraint_system<Ft>* cs = NULL) {
    // try reading from file
    
    ifstream ek_data(ekfile);
    if (!ek_data.is_open()) return NULL;

    int sz1;
    ek_data >> sz1;
    
    // initial check to eliminate obvious non-matches
    if (cs!=NULL && (sz1!=cs->constraints.size())) return NULL;
        
    libsnark::r1cs_gg_ppzksnark_keypair<libsnark::default_r1cs_gg_ppzksnark_pp>* keys = 
        new libsnark::r1cs_gg_ppzksnark_keypair<libsnark::default_r1cs_gg_ppzksnark_pp>();
    
    ek_data >> keys->pk;
    ek_data >> keys->vk;
    ek_data.close();
    
    if (cs!=NULL && !cseq(keys->pk.constraint_system, *cs)) {
        delete keys;
        return NULL;
    }
    
    return keys;
}
    
void zkgg_write_keys(const libsnark::r1cs_gg_ppzksnark_keypair<libsnark::default_r1cs_gg_ppzksnark_pp>& keypair,
            const char* vkfile = NULL, const char* ekfile = NULL) {
    if (vkfile && *vkfile) {
        ofstream vk_data(vkfile);
        prettywrite(vk_data, keypair.vk);
        
        // snarkjs puts this in the ver key so for compatibility we do the same...
        prettywrite(vk_data, keypair.pk.alpha_g1);
        prettywrite(vk_data, keypair.pk.beta_g2);

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
    
void zkgg_write_proof(
    const libsnark::r1cs_gg_ppzksnark_proof<libsnark::default_r1cs_gg_ppzksnark_pp>& proof,
    const libsnark::r1cs_primary_input<Ft> pubvals,
    const char* logfile
) {
    ofstream prooffile(logfile);

    prooffile << pubvals.size() << endl;
    for (auto &it: pubvals) { prettywrite(prooffile, it); prooffile << endl; }

    prettywrite(prooffile, proof.g_A);
    prettywrite(prooffile, proof.g_B);
    prettywrite(prooffile, proof.g_C);

    prooffile.close();
}


%}
