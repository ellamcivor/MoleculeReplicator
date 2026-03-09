import molecule
import ctypes
import io

header = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">"""

footer = """</svg>"""

offsetx = 500
offsety = 500

# return ith line in list
def getLine(i, lines):
    return lines[i].rstrip('\r\n')


class Atom:

    def __init__( self, c_atom ): 
        self.atom = c_atom
        self.z = c_atom.z


    def __str__( self ):
        return f"Name: {self.atom.element}, x: {self.atom.x}, y: {self.atom.y}, z: {self.atom.z}"
        

    def svg( self ):
        x_coord = self.atom.x * 100.0 + offsetx 
        y_coord = self.atom.y * 100.0 + offsety

        rad = radius["other"]

        if self.atom.element in radius.keys():
            rad = radius[self.atom.element]

        colour = self.atom.element

        if self.atom.element in element_name.keys():
            colour = element_name[self.atom.element]
        
        return '  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' % (x_coord, y_coord, rad, colour)
    


class Bond:

    def __init__( self, c_bond ):
        self.bond = c_bond
        self.z = c_bond.z


    def __str__( self ):
        bond_str = f"Atom 1: {self.bond.a1} \nx1: {self.bond.x1}, y1: {self.bond.y1}\n"
        bond_str = bond_str + f"Atom 2: {self.bond.a2} \nx2: {self.bond.x2}, y2: {self.bond.y2}\n"
        bond_str = bond_str + f"z: {self.bond.z}, len: {self.bond.len}, dx: {self.bond.dx}, dy: {self.bond.dy}"
        return bond_str
    

    def svg( self ):
        x1_centre = self.bond.x1 * 100.0 + offsetx
        y1_centre = self.bond.y1 * 100.0 + offsety 

        x2_centre = self.bond.x2 * 100.0 + offsetx
        y2_centre = self.bond.y2 * 100.0 + offsety

        dx = -(self.bond.dy)
        dy = self.bond.dx

        x1a = x1_centre + 10 * dx
        y1a = y1_centre + 10 * dy
        x1b = x1_centre - 10 * dx
        y1b = y1_centre - 10 * dy
        x2a = x2_centre + 10 * dx
        y2a = y2_centre + 10 * dy
        x2b = x2_centre - 10 * dx
        y2b = y2_centre - 10 * dy

        return '  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' %(x1a, y1a, x1b, y1b, x2b, y2b, x2a, y2a)


class Molecule( molecule.molecule ):

    def __str__( self ):
        
        mol_str = "Atoms:\n"

        for i in range(self.atom_no):
            atom = Atom(self.get_atom(i))
            mol_str = mol_str + atom.__str__() + '\n'

        mol_str = mol_str + "\nBonds:\n"

        for i in range(self.bond_no):
            bond = Bond(self.get_bond(i))
            mol_str = mol_str + bond.__str__() + '\n'
    
        return mol_str
        

    def svg( self ):
        svg = header 

        i = 0
        j = 0

        # sort atoms and bonds by z value
        while ((i < self.atom_no) and (j < self.bond_no)):
            atom = Atom(self.get_atom(i))
            bond = Bond(self.get_bond(j))

            if (atom.z < bond.z):
                svg = svg + atom.svg()
                i += 1
            else:
                svg = svg + bond.svg()
                j += 1

        # add remaining atoms and bonds
        if (i == self.atom_no):
            for k in range (j, self.bond_no):
                bond = Bond(self.get_bond(k))
                svg = svg + bond.svg()
        else:
            for k in range(i, self.atom_no):
                atom = Atom(self.get_atom(k))
                svg = svg + atom.svg()

        svg = svg + footer

        return svg


    def parse( self, f ):

        lines = f.readlines()

        # read count line block
        line = getLine(3, lines)

        # number of atoms
        val = line[:3]
        atom_no = int(val)

        # number of bonds
        val = line[3:6]
        bond_no = int(val)

        # read atoms
        for i in range(4, atom_no + 4):
            line = getLine(i, lines)

            # x value
            val = line[:10]
            x = float(val)

            # y value
            val = line[10:20]
            y = float(val)

            # z value
            val = line[20:30]
            z = float(val)

            # name
            val = line[31:34]
            name = line[31]

            self.append_atom( name, x, y, z )
    
        # read bonds
        for i in range (atom_no + 4, bond_no + atom_no + 4):
            line = getLine(i, lines)

            # atom 1
            val = line[:3]
            a1 = int(val) - 1

            # atom 2
            val = line[3:6]
            a2 = int(val) - 1

            # epairs
            val = line[6:9]
            epairs = int(val)

            self.append_bond( a1, a2, epairs )
            