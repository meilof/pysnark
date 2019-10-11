Python3 bindings for libsnark. Minimal example:

```
cd build
cmake ..
make 
cp ../examples/test.py .
python3 test.py
```

Magical line for Mac OS

```
cmake -DCMAKE_PREFIX_PATH=/usr/local/Cellar/openssl/1.0.2t -DCMAKE_SHARED_LINKER_FLAGS=-L/usr/local/Cellar/openssl/1.0.2t/lib -DWITH_PROCPS=OFF -DWITH_SUPERCOP=OFF -DOPT_FLAGS=-std=c++11 -DPYTHON_EXECUTABLE=/usr/local/opt/python/bin/python3.7 ..
```


