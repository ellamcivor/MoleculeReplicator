import os;
import sqlite3;
import MolDisplay

increment_tables = ( 'Atoms', 'Bonds', 'Molecules' )

columns = { 
  'Atoms': 'ELEMENT_CODE, X, Y, Z',
  'Bonds': 'A1, A2, EPAIRS',
  'Molecules': 'NAME'
}

class Database:
    
  def __init__( self, reset=False ):

    if reset:
      try:
        os.remove( 'molecules.db' )
      except OSError:
        pass

    self.conn = sqlite3.connect( 'molecules.db' )


  def create_tables( self ):

    # get existing tables
    data = self.conn.execute( """SELECT name FROM sqlite_master WHERE type='table';""" )
    existing_tables = data.fetchall()
    existing_tables = [table[0] for table in existing_tables]

    if 'Elements' not in existing_tables:
      self.conn.execute( """CREATE TABLE Elements 
                  ( ELEMENT_NO     INTEGER NOT NULL,
                  ELEMENT_CODE   VARCHAR(3) NOT NULL,
                  ELEMENT_NAME   VARCHAR(32) NOT NULL,
                  COLOUR1        CHAR(6) NOT NULL,
                  COLOUR2      CHAR(6) NOT NULL,
                  COLOUR3        CHAR(6) NOT NULL,
                  RADIUS         DECIMAL(3) NOT NULL,
                  PRIMARY KEY (ELEMENT_CODE) );""" )
    
    if 'Atoms' not in existing_tables:
      self.conn.execute( """CREATE TABLE Atoms 
                  ( ATOM_ID        INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                  ELEMENT_CODE   VARCHAR(3) NOT NULL,
                  X              DECIMAL(7,4) NOT NULL,
                  Y            DECIMAL(7,4) NOT NULL,
                  Z              DECIMAL(7,4) NOT NULL,
                  FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements );""" )

    if 'Bonds' not in existing_tables:
      self.conn.execute( """CREATE TABLE Bonds 
                  ( BOND_ID        INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                  A1             INTEGER NOT NULL,
                  A2             INTEGER NOT NULL,
                  EPAIRS         INTEGER NOT NULL );""" )
    
    if 'Molecules' not in existing_tables:
      self.conn.execute( """CREATE TABLE Molecules 
                  ( MOLECULE_ID  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                  NAME         TEXT NOT NULL UNIQUE );""" )
      
    if 'MoleculeAtom' not in existing_tables:
      self.conn.execute( """CREATE TABLE MoleculeAtom 
                  ( MOLECULE_ID    INTEGER NOT NULL,
                  ATOM_ID      INTEGER NOT NULL,
                  PRIMARY KEY (MOLECULE_ID,ATOM_ID),
                  FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules,
                  FOREIGN KEY (ATOM_ID) REFERENCES Atoms );""" )
    
    if 'MoleculeBond' not in existing_tables:
      self.conn.execute( """CREATE TABLE MoleculeBond 
                  ( MOLECULE_ID  INTEGER NOT NULL,
                  BOND_ID      INTEGER NOT NULL,
                  PRIMARY KEY (MOLECULE_ID,BOND_ID),
                  FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules,
                  FOREIGN KEY (BOND_ID) REFERENCES Bonds );""" )


  def __setitem__( self, table, values ):

    vals = ','.join(['?']*len(values))

    # if table has autoincrement column exclude that column from insert
    if table not in increment_tables:
      query = f'INSERT INTO {table} VALUES ({vals})'
    else:
      query = f'INSERT INTO {table} ({columns[table]}) VALUES ({vals})'

    self.conn.execute(query, values)
    self.conn.commit()


  def add_atom( self, molname, atom ):

    # add atom to Atoms
    self['Atoms'] = ( atom.element, atom.x, atom.y, atom.z )

    atom_id = self.conn.execute( """SELECT last_insert_rowid()""" ).fetchone()[0]

    # link atom to MoleculeAtom
    molecule_id = self.conn.execute( """SELECT MOLECULE_ID 
                         FROM Molecules 
                         WHERE NAME='%s'""" % (molname) ).fetchone()[0]

    self['MoleculeAtom'] = ( molecule_id, atom_id )
  

  def add_bond( self, molname, bond ):

    # add bond to Bonds
    self['Bonds'] = ( bond.a1, bond.a2, bond.epairs )

    bond_id = self.conn.execute( """SELECT last_insert_rowid()""" ).fetchone()[0]

    # link bond to MoleculeBond
    molecule_id = self.conn.execute( """SELECT MOLECULE_ID 
                 FROM Molecules 
                 WHERE NAME='%s'""" % (molname) ).fetchone()[0]

    self['MoleculeBond'] = ( molecule_id, bond_id )
  

  def add_molecule( self, name, fp ):

    # create mol object from file and add to Molecules table
    mol = MolDisplay.Molecule()
    mol.parse(fp)

    self['Molecules'] = ( name, )
    
    # add mol's atoms and bonds to their tables
    for i in range(mol.atom_no):
      self.add_atom( name, mol.get_atom(i) )

    for i in range(mol.bond_no):
      self.add_bond( name, mol.get_bond(i) )

  
  def load_mol( self, name ):

    mol = MolDisplay.Molecule()

    # get atoms from table to add to mol object
    atoms = self.conn.execute( """SELECT ELEMENT_CODE, X, Y, Z 
                         FROM Molecules as M, MoleculeAtom as MA, Atoms as A
                         WHERE M.MOLECULE_ID = MA.MOLECULE_ID
                          AND MA.ATOM_ID = A.ATOM_ID
                          AND NAME='%s'""" % (name) ).fetchall()
    
    for atom in atoms:
      mol.append_atom( atom[0], atom[1], atom[2], atom[3] )

    # get bonds from table to add to mol object
    bonds = self.conn.execute( """SELECT A1, A2, EPAIRS
                    FROM Molecules as M, MoleculeBond as MB, Bonds as B
                    WHERE M.MOLECULE_ID = MB.MOLECULE_ID
                    AND MB.BOND_ID = B.BOND_ID
                    AND NAME='%s'""" % (name) ).fetchall()
    
    for bond in bonds:
      mol.append_bond( bond[0], bond[1], bond[2] )

    return mol
  

  def radius( self ):

    radius_data = self.conn.execute( """ SELECT ELEMENT_CODE, RADIUS
                       FROM Elements """ ).fetchall()
    
    rad_dict = {}

    for element, radius in radius_data:
      rad_dict[element] = radius

    rad_dict["other"] = 30

    return rad_dict


  def element_name( self ):

    element_data = self.conn.execute( """ SELECT ELEMENT_CODE, ELEMENT_NAME
                        FROM Elements """ ).fetchall()
  
    name_dict = {}

    for element_code, element_name in element_data:
      name_dict[element_code] = element_name

    name_dict["other"] = "Other"
    
    return name_dict


  def radial_gradients( self ):

    data = self.conn.execute( """ SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3
                    from Elements """ ).fetchall()

    radialGradientSVG = ""

    # append string to radialGradientSVG for each element in table
    for name, c1, c2, c3 in data:
      radialGradientSVG += """
        <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">"
        <stop offset="0%%" stop-color="#%s"/>
        <stop offset="50%%" stop-color="#%s"/>
        <stop offset="100%%" stop-color="#%s"/>
        </radialGradient>""" % (name, c1, c2, c3)

    return radialGradientSVG
  

  # searches database for any atoms of element not in database
  # and gives them default colours
  def default_gradients( self, mol ):

    def_colours = ""

    e_codes = self.conn.execute("""SELECT ELEMENT_CODE FROM Elements""").fetchall()

    for i in range(0, mol.atom_no):
      j = 0
      for element in e_codes:
        if mol.get_atom(i).element == element[0]:
          j += 1
      if j != len(e_codes):
        # give default colour
        def_colours += """
      <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">"
        <stop offset="0%%" stop-color="#FFFFFF"/>
        <stop offset="50%%" stop-color="#000020"/>
        <stop offset="100%%" stop-color="#000000"/>
        </radialGradient>""" % (mol.get_atom(i).element)

    return def_colours
  

  # creates html code for display of element table
  def element_display( self ):
    html_str = """
<table id="elements">
  <tr id="element_head">
    <td>#</td>
    <td>Symbol</td>
    <td>Name</td>
    <td>C1</td>
    <td>C2</td>
    <td>C3</td>
    <td>Radius</td>
  </tr>
"""
    elements = self.conn.execute( "SELECT * FROM Elements" ).fetchall()

    for element in elements:
      html_str += """  <tr class="row">\n"""

      i = 1
      for val in element:
        if i == 2:
          html_str += """    <td class="e_code">%s</td>\n""" % (val)
        else :
          html_str += """    <td>%s</td>\n""" % (val)
        i += 1

      html_str += """  </tr>\n"""
      
    html_str += """</table>\n"""

    return html_str
  

  def molecule_display( self ):
    html_str = """
<table id="molecules">
  <tr id="molecule_head">
    <td>Molecule</td>
    <td>Atom Number</td>
    <td>Bond Number</td>
  </tr>"""
    names = self.conn.execute( "SELECT Name FROM Molecules" ).fetchall()

    for name in names:
      atoms = self.conn.execute( """SELECT ELEMENT_CODE
                    FROM Molecules as M, MoleculeAtom as MA, Atoms as A
                    WHERE M.MOLECULE_ID = MA.MOLECULE_ID
                    AND MA.ATOM_ID = A.ATOM_ID
                    AND M.NAME='%s'""" % (name) ).fetchall()
      
      bonds = self.conn.execute( """SELECT A1
                    FROM Molecules as M, MoleculeBond as MB, Bonds as B
                    WHERE M.MOLECULE_ID = MB.MOLECULE_ID
                    AND MB.BOND_ID = B.BOND_ID
                    AND M.NAME='%s'""" % (name) ).fetchall()

      html_str += """
  <tr class="row">
    <td class="m_name">%s</td> 
    <td>%s</td>
    <td>%s</td>
  </tr>""" % (name[0], len(atoms), len(bonds))
      
    html_str += """\n</table>\n"""

    return html_str
  

  def removeElement( self, code ):
    
    self.conn.execute( """DELETE FROM Elements
                WHERE ELEMENT_CODE = '%s'""" % (code))
    
