%{

#include <iostream>
#include <fstream>

template<mp_size_t n, const bigint<n>& modulus>
void prettywrite(std::ostream &strm, const Fp_model<n, modulus> &val) {
    mpz_t t;
    mpz_init(t);
    val.as_bigint().to_mpz(t);
    strm << t;
    mpz_clear(t);       
}
    
template<mp_size_t n, const bigint<n>& modulus>
void prettywrite(std::ostream &strm, const Fp2_model<n, modulus> &el)
{
    prettywrite(strm, el.c0);
    strm << " ";
    prettywrite(strm, el.c1);
}
    
// formatting by https://github.com/christianlundkvist/libsnark-tutorial/blob/master/src/util.hpp

void prettywrite(ostream& strm, const libff::G1<default_r1cs_ppzksnark_pp>& pt) {
    libff::G1<default_r1cs_ppzksnark_pp> pp(pt);
    pp.to_affine_coordinates();
    prettywrite(strm, pp.X); strm << endl;
    prettywrite(strm, pp.Y); strm << endl;
}
    
void prettywrite(ostream& strm, const libff::G2<default_r1cs_ppzksnark_pp>& pt) {
    libff::G2<default_r1cs_ppzksnark_pp> pp(pt);
    pp.to_affine_coordinates();
    prettywrite(strm, pp.X); strm << endl;
    prettywrite(strm, pp.Y); strm << endl;
}

template<typename T>
void prettywrite(std::ostream& out, const sparse_vector<T> &v)
{
    for (int i = 0; i < v.indices.size(); i++) {
        prettywrite(out, v.values[i]);
    }
}
    
template<typename T>
void prettywrite(std::ostream& out, const accumulation_vector<T> &v)
{
    out << (v.rest.indices.size()+1) << endl;
    prettywrite(out, v.first);
    prettywrite(out, v.rest);
}
    
bool cseq(
    const libsnark::r1cs_constraint_system<Ft>& cs1,
    const libsnark::r1cs_constraint_system<Ft>& cs2) {
    if (cs1.constraints.size() != cs2.constraints.size()) return false;
    if (cs1.primary_input_size != cs2.primary_input_size) return false;
    if (cs1.auxiliary_input_size != cs2.auxiliary_input_size) return false;
    
    auto it1 = cs1.constraints.begin();
    auto it2 = cs2.constraints.begin();
    
    // libsnark may swap a and b so this is a bit involved
    while (it1!=cs1.constraints.end()) {
        if (!(it1->c==it2->c)) return false;
        if (it1->a==it2->a) {
            if (!(it1->b==it2->b)) return false;
        } else {
            if (!(it1->a==it2->b && it1->b==it2->a)) return false;
        }
        it1++;
        it2++;
    }
    return true;
}
    
%}

