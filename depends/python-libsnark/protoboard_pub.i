%inline %{

class ProtoboardPub: public libsnark::protoboard<Ft> {
    vector<var_index_t> pubixs;
public:

    void setpublic(const libsnark::pb_variable<Ft> &var) {
        if (pubixs.size()>0 && pubixs.back()>=var.index) {
            cerr << "*** setpublic: pb_variables should be marked public in order, ignoring" << endl;
        } else {
            pubixs.push_back(var.index);
        }
    }
    
    libsnark::r1cs_constraint_system<Ft> get_constraint_system_pubs() {
        r1cs_constraint_system<Ft> pbcs = get_constraint_system();
        r1cs_constraint_system<Ft> cs;
        
        // build translation table
        int ntot = num_variables();
        vector<int> table(ntot+1);
        int cur = 1, curpub = 1, curshift = pubixs.size();
        table[0] = 0;
        for (auto const& ix: pubixs) {
            while (cur<ix) {
                table[cur] = cur+curshift;
                cur++;
            }
            table[cur++] = curpub++;
            curshift--;
        }
        while (cur <= ntot) {
            table[cur] = cur;
            cur++;
        }
        
        // reorganize constraint system
        for (auto csi: pbcs.constraints) {
            for (auto &ai: csi.a.terms) ai.index = table[ai.index];
            for (auto &bi: csi.b.terms) bi.index = table[bi.index];
            for (auto &ci: csi.c.terms) ci.index = table[ci.index];
            cs.add_constraint(csi);
        }
    
        cs.primary_input_size = pubixs.size();
        cs.auxiliary_input_size = num_variables() - pubixs.size();

        return cs;
    }
    
    libsnark::r1cs_primary_input<Ft> primary_input_pubs() {
        r1cs_primary_input<Ft> ret;
        for (auto const& ix: pubixs) {
            ret.push_back(full_variable_assignment()[ix-1]);
        }
        return ret;
    }
    
    libsnark::r1cs_auxiliary_input<Ft> auxiliary_input_pubs() {
        r1cs_auxiliary_input<Ft> ret;
        
        int ix = 1;
        vector<var_index_t>::iterator it = pubixs.begin();
        for (auto const& val: full_variable_assignment()) {
            if (it != pubixs.end() && *it==ix) {
                it++;
            } else {
                ret.push_back(val);
            }
            ix++;
        }
        return ret;
    }
    
};


%}