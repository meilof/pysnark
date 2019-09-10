# cflags/ldflags for tools
CFLAGS=-std=c++11 -DSUPPORT_SNARK -I ate-pairing/include
LDFLAGS=-L ate-pairing/lib -L/usr/local/lib -lm -lzm -lgmpxx -lgmp


EXECS=qapgen qapcoeffcache qapgenf qapinput qapprove qapver

all: $(EXECS)	

%.o: %.cpp
	g++ $(CFLAGS) -c -o $@ $<

qapgen: qapgen.o key.o proof.o modp.o base.o qap2key.o fft.o
	g++ -o $@ $^ $(LDFLAGS)
	
qapcoeffcache: qapcoeffcache.o key.o proof.o modp.o base.o qap2key.o fft.o
	g++ -o $@ $^ $(LDFLAGS)

qapgenf: qapgenf.o key.o qap.o modp.o base.o qap2key.o fft.o
	g++ -o $@ $^ $(LDFLAGS) 
	
qapinput: qapinput.o base.o key.o proof.o prove.o qap2key.o modp.o fft.o
	g++ -o $@ $^ $(LDFLAGS) 

qapprove: qapprove.o base.o key.o modp.o proof.o prove.o qap.o modp.o fft.o
	g++ -o $@ $^ $(LDFLAGS) 

qapver: qapver.o base.o key.o prove.o proof.o verify.o modp.o qap.o fft.o
	g++ -o $@ $^ $(LDFLAGS) 

clean:
	rm -f *.o $(EXECS)
