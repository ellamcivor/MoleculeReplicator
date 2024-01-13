CC = clang
CFLAGS = -Wall -std=c99 -pedantic

all: mol.o libmol.so molecule_wrap.c molecule_wrap.o _molecule.so

clean:
	rm -f *.o *.so myprog

libmol.so: mol.o 
	$(CC) mol.o -shared -o libmol.so

mol.o: mol.c mol.h
	$(CC) $(CFLAGS) -c mol.c -fPIC -o mol.o  

molecule_wrap.c: molecule.i
	swig3.0 -python molecule.i

molecule_wrap.o: molecule_wrap.c 
	$(CC) -fPIC -c -I/usr/include/python3.7m molecule_wrap.c -o molecule_wrap.o

_molecule.so: molecule_wrap.o 
	$(CC) -shared -dynamicLib -L./ -lmol -L/usr/lib/python3.7/config-3.7m-x86_64-linux-gnu -lpython3.7m molecule_wrap.o -o _molecule.so



