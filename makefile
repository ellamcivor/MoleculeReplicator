CC = clang
CFLAGS = -Wall -std=c99 -pedantic
PYTHON = Library/Frameworks/Python.framework/Versions/3.11/include/python3.11
PYLIB = Library/Frameworks/Python.framework/Versions/3.11/lib

all: mol.o libmol.so molecule_wrap.c molecule_wrap.o _molecule.so

clean:
	rm -f *.o *.so myprog

libmol.so: mol.o 
	$(CC) mol.o -shared -o libmol.so

mol.o: mol.c mol.h
	$(CC) $(CFLAGS) -c mol.c -fPIC -o mol.o  

molecule_wrap.c: molecule.i
	swig -python molecule.i

molecule_wrap.o: molecule_wrap.c 
	$(CC) -fPIC -c -I/$(PYTHON) molecule_wrap.c -o molecule_wrap.o

_molecule.so: molecule_wrap.o 
	$(CC) -shared -dynamicLib -L./ -lmol -L/$(PYLIB) -lpython3.11 molecule_wrap.o -o _molecule.so



