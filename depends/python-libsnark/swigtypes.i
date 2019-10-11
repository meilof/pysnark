%typemap(typecheck, precedence=3000) Ft const& {
  $1 = PyLong_Check($input) ? 1 : 0;
}

%typemap(in, precedence=3000) Ft const& {
    long val;
    int overflow;
    val = PyLong_AsLongAndOverflow($input, &overflow);
    
    if (val!=-1 || (overflow==0 && !PyErr_Occurred())) {
        $1 = new Ft(val);
    } else {
        PyObject *str = PyObject_Str($input);
        if (!str) { SWIG_fail; }
    
        const char* cstr = PyUnicode_AsUTF8(str);
        if (!cstr) { Py_DECREF(str); SWIG_fail; }
        
        $1 = new Ft(libff::bigint<Ft::num_limbs>(cstr));    
        Py_DECREF(str);
    }
}

%typemap(out, precedence=3000) Ft{
    stringstream ss;
    
    mpz_t t;
    mpz_init(t);
    $1.as_bigint().to_mpz(t);
    ss << t;
    mpz_clear(t);
    
    $result = PyLong_FromString(ss.str().c_str(), NULL, 10);    
}

%typemap(out, precedence=3001) libff::bigint<Ft::num_limbs> {
    stringstream ss;
    
    mpz_t t;
    mpz_init(t);
    $1.to_mpz(t);
    ss << t;
    mpz_clear(t);
    
    $result = PyLong_FromString(ss.str().c_str(), NULL, 10);    
}

