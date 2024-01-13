#include "mol.h"

void atomset ( atom *atom, char element[3], double *x, double *y, double *z ) {
    strcpy( atom->element, element );
    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
}

void atomget( atom *atom, char element[3], double *x, double *y, double *z ) {
    strcpy( element, atom->element );
    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
}

void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char * epairs ) { 
    bond->a1 = *a1;
    bond->a2 = *a2;

    bond->atoms = *atoms;
    bond->epairs = *epairs;

    compute_coords(bond);
}

void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom ** atoms, unsigned char * epairs ) {
    *a1 = bond->a1;
    *a2 = bond->a2;

    *atoms = bond->atoms;
    *epairs = bond->epairs;
}

void compute_coords( bond * bond ) {
    bond->x1 = bond->atoms[bond->a1].x;
    bond->y1 = bond->atoms[bond->a1].y;

    bond->x2 = bond->atoms[bond->a2].x;
    bond->y2 = bond->atoms[bond->a2].y;
    
    bond->z = (bond->atoms[bond->a1].z + bond->atoms[bond->a2].z) / 2;

    bond->len = sqrt(pow(bond->x2 - bond->x1, 2) + pow(bond->y2 - bond->y1, 2));

    bond->dx = (bond->x2 - bond->x1) / (bond->len);
    bond->dy = (bond->y2 - bond->y1) / (bond->len);
}

molecule *molmalloc( unsigned short atom_max, unsigned short bond_max ) {
    molecule *mol_pointer = (struct molecule*) malloc(sizeof(struct molecule));

    mol_pointer->atom_max = atom_max;
    mol_pointer->atom_no = 0;
    mol_pointer->atoms = (struct atom*) malloc(sizeof(struct atom) * atom_max);
    mol_pointer->atom_ptrs = (struct atom**) malloc(sizeof(struct atom*) * atom_max);
    
    mol_pointer->bond_max = bond_max;
    mol_pointer->bond_no = 0;
    mol_pointer->bonds = (struct bond*) malloc(sizeof(struct bond) * bond_max);
    mol_pointer->bond_ptrs = (struct bond**) malloc(sizeof(struct bond*) * bond_max);

    return mol_pointer;
}

molecule *molcopy( molecule *src ) {
    molecule *mol_ptr = molmalloc( src->atom_max, src->bond_max );

    if (mol_ptr == NULL) {
        return NULL;
    }

    for (int i = 0; i < src->atom_no; i++) {
        molappend_atom( mol_ptr, &(src->atoms[i]) );
    }

    for (int i = 0; i < src->bond_no; i++) {
        molappend_bond( mol_ptr, &(src->bonds[i]) );

        /* make atoms in new bond point to the new molecule's atoms 
            rather than the old molecule's atoms by determining which 
            atoms are being pointed to in old molecule's bond */
        mol_ptr->bonds[i].atoms = mol_ptr->atoms;
    }

    return mol_ptr;
}

void molfree( molecule *ptr ) {
    free( ptr->bond_ptrs );
    free( ptr->bonds );
    free( ptr->atom_ptrs );
    free( ptr->atoms );
    free( ptr );
}

void molappend_atom( molecule *molecule, atom *atom ) {
    int increased = 0;
    
    if (molecule->atom_no == molecule->atom_max) {
        increased = 1;
        int new_size;

        if (molecule->atom_max == 0) {
            new_size = 1;
        } else {
            new_size = molecule->atom_max * 2;
        }

        molecule->atom_max = new_size;
        molecule->atoms = (struct atom*) realloc(molecule->atoms, sizeof(struct atom) * new_size);
        molecule->atom_ptrs = (struct atom**) realloc(molecule->atom_ptrs, sizeof(struct atom*) * new_size);
    }
    
    molecule->atoms[molecule->atom_no] = *atom;

    // if reallocated change all pointers, else only set up new pointer
    if (increased == 1) {
        for (int i = 0; i <= molecule->atom_no; i++) {
            molecule->atom_ptrs[i] = &(molecule->atoms[i]);
        }  
    } else {
        molecule->atom_ptrs[molecule->atom_no] = &(molecule->atoms[molecule->atom_no]);
    }    

    molecule->atom_no++;
}

void molappend_bond( molecule *molecule, bond *bond ) {
    int increased = 0;

    if (molecule->bond_no == molecule->bond_max) {
        increased = 1;
        int new_size;

        if (molecule->bond_max == 0) {
            new_size = 1;
        } else {
            new_size = molecule->bond_max * 2;
        }
        
        molecule->bond_max = new_size;
        molecule->bonds = (struct bond*) realloc(molecule->bonds, sizeof(struct bond) * new_size);
        molecule->bond_ptrs = (struct bond**) realloc(molecule->bond_ptrs, sizeof(struct bond*) * new_size);
    }

    molecule->bonds[molecule->bond_no] = *bond;

    // if reallocated change all pointers, else only set up new pointer
    if (increased == 1) {
        for (int i = 0; i <= molecule->bond_no; i++) {
            molecule->bond_ptrs[i] = &(molecule->bonds[i]);
        }
    } else {
        molecule->bond_ptrs[molecule->bond_no] = &(molecule->bonds[molecule->bond_no]);
    }

    molecule->bond_no++;
}

void molsort( molecule *molecule ) {
    qsort( molecule->atom_ptrs, molecule->atom_no, sizeof(struct atom *), atom_comp );
    qsort( molecule->bond_ptrs, molecule->bond_no, sizeof(struct bond *), bond_comp );
}

int atom_comp( const void *a, const void *b ) {
    struct atom *a_ptr, *b_ptr;
    int comparison;

    a_ptr = *(struct atom **)a;
    b_ptr = *(struct atom **)b;

    if (a_ptr->z < b_ptr->z) {
        comparison = -1;
    }
    else if (a_ptr->z > b_ptr->z) {
        comparison = 1;
    }
    else {
        comparison = 0;
    }

    return comparison;
}

int bond_comp( const void *a, const void *b ) {
    struct bond *a_ptr, *b_ptr;
    int comparison;

    a_ptr = *(struct bond **)a;
    b_ptr = *(struct bond **)b;

    if (a_ptr->z < b_ptr->z) {
        comparison = -1;
    }
    else if (a_ptr->z > b_ptr->z) {
        comparison = 1;
    }
    else {
        comparison = 0;
    }

    return comparison;
}

void xrotation( xform_matrix xform_matrix, unsigned short deg ) {
    double theta = (double) (deg * PI) / 180;

    xform_matrix[0][0] = 1;
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = 0;
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = cos(theta);
    xform_matrix[1][2] = sin(theta) * (-1);
    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = sin(theta);
    xform_matrix[2][2] = cos(theta);
}

void yrotation( xform_matrix xform_matrix, unsigned short deg ) {
    double theta = (double) (deg * PI) / 180;

    xform_matrix[0][0] = cos(theta);
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = sin(theta);
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = 1;
    xform_matrix[1][2] = 0;
    xform_matrix[2][0] = sin(theta) * (-1);
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = cos(theta);
}

void zrotation( xform_matrix xform_matrix, unsigned short deg ) {
    double theta = (double) (deg * PI) / 180;

    xform_matrix[0][0] = cos(theta);
    xform_matrix[0][1] = sin(theta) * (-1);
    xform_matrix[0][2] = 0;
    xform_matrix[1][0] = sin(theta);
    xform_matrix[1][1] = cos(theta);
    xform_matrix[1][2] = 0;
    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = 1;
}

void mol_xform( molecule *molecule, xform_matrix matrix ) {

    for (int i = 0; i < molecule->atom_no; i++) {
        double x = molecule->atoms[i].x;
        double y = molecule->atoms[i].y;
        double z = molecule->atoms[i].z;

        molecule->atoms[i].x = (matrix[0][0] * x) + (matrix[0][1] * y) +
                                (matrix[0][2] * z);
        molecule->atoms[i].y = (matrix[1][0] * x) + (matrix[1][1] * y) +
                                (matrix[1][2] * z);
        molecule->atoms[i].z = (matrix[2][0] * x) + (matrix[2][1] * y) + 
                                (matrix[2][2] * z);

    }

    for (int i = 0; i < molecule->bond_no; i++) {
        compute_coords(&(molecule->bonds[i]));
    }

}

rotations *spin( molecule *mol ) {
    printf("Spin: To do\n");
    return NULL;
}

void rotationsfree( rotations *rotations ) {
    printf("Rotations free: To do\n");
}



