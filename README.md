# MoleculeReplicator
Ella McIvor
2023

## About

This is an application that takes SDF files of molecules and converts them to SVG 
images. The user may run the server on their local computer and view the website in 
their web browser.

## Required Files

* mol.h:
	* header file used in mol.c that contains typedefs, structure definitions
	  and function prototypes

* mol.c:
	* C library for molecule position calculations

* molecule.i:
	* interfaces C code with Python code

* MolDisplay.py:
	* Python library to generate SVG images of molecules

* molsql.py:
	* supports database operation

* server.py:
	* web server for adding elements, molecules and uploading SDF files

* element_view.html:
	* HTML page for adding, deleting and viewing elements
	* Asks for the following information regarding an element:
		* **#**: The number corresponding to the element in the periodic table
		* **Symbol**: The symbol corresponding to the element in the periodic table
		* **C1**: The hexadecimal value for the red value of the element colour
		* **C2**: The hexadecimal value for the green value of the element colour
		* **C3**: The hexadecimal value for the blue value of the element colour
		* **Radius**: The radius of the element 


* mol_view.html:
	* HTML page for viewing molecule information

* sdf_upload.html:
	* HTML page for uploading SDF files that will be addedw to molecule list

* svg_view.html:
	* HTML page for viewing and rotating a selected molecule

* style.css:
	* controls style of all HTML pages

* script.js: 
	* deals with front-end functionality of website 

* makefile:
	* contains instructions for the following targets:
		* mol.o -- position independent (-fpic) object code file created 
		  from mol.c
		* libmol.so -- shared library (-shared) created from mol.o
		* molecule_wrap.c and molecule.py -- a pair of files that provide a Python
		  interface to C code (generated using swig program base and molecule.i)
		* molecule_wrap.o -- object file that is an object library to interface
		  with C code
		* _molecule.so -- shared object library used by molecule.py to interface
		  between C and Python
		* clean -- deletes all .o, .so, and executable files
	* the PYTHON and PYLIB paths were generated for MacOS and may need to be changed to
	  fit your personal computer and operating system

## Testing:

* You may use the following values for elements that will 
  be included in the example SDF files. Add these values
  on the element view page:
  
  **#**: 1
  **Symbol**: H
  **Name**: Hydrogen
  **C1**: FFFFFF
  **C2**: 050505
  **C3**: 020202
  **Radius**: 25

  **#**: 6
  **Symbol**: C
  **Name**: Carbon
  **C1**: 808080
  **C2**: 010101
  **C3**: 000000
  **Radius**: 40

  **#**: 7
  **Symbol**: N
  **Name**: Nitrogen
  **C1**: 0000FF
  **C2**: 000005
  **C3**: 000002
  **Radius**: 40

  **#**: 8
  **Symbol**: O
  **Name**: Oyxgen
  **C1**: FF0000
  **C2**: 050000
  **C3**: 020000
  **Radius**: 40

* SDF Files to Upload
	* caffeine-3D-structure-CT1001987571.sdf:
		* SDF representation of Caffeine molecule
	* water-3D-structure-CT1000292221.sdf
		* SDF representation of Caffeine molecule


## Compiling

Use "make" command with the given makefile.
**Note:** Refer to "Required Files" section: Paths within the makefile may need to be changed to accomodate the computer on which the application is running.

## Running

**Command line:** python3 server.py < port# >
**Web browser:** http://localhost:51334/element_view.html

## Limitations

* SDF files must be in the same directory as the code

