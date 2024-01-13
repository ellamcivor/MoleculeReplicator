from http.server import HTTPServer, BaseHTTPRequestHandler

import sys
import urllib
import sqlite3

import molsql
import MolDisplay
import molecule

public_files = { '/element_view.html', '/mol_view.html', '/sdf_upload.html', '/svg_view.html', '/style.css', '/script.js' }

# database variable
db = molsql.Database(reset=False)
db.create_tables()

svg_code = ""

class MyHandler( BaseHTTPRequestHandler ):
    
    def do_GET( self ):

        # display element page
        if self.path in public_files:
            self.send_response( 200 )
            self.send_header( "Content-type", "text/html" )

            fp = open( self.path[1:] )

            page = fp.read()
            fp.close()

            # retrieve tables from database in html format
            e_table = db.element_display()
            mol_table = db.molecule_display()

            # place tables into html code
            page = page.replace( '{element_table}', e_table )
            page = page.replace( '{molecule_table}', mol_table )
            page = page.replace( '{svg_image}', svg_code )


            self.send_header( "Content-length", len(page) )
            self.end_headers()

            self.wfile.write( bytes( page, "utf-8") )
        
        else:
            self.send_response( 404 )
            self.end_headers()
            self.wfile.write( bytes( "404: not found", "utf-8" ) )
    
    def do_POST( self ):
        
        if self.path == "/element_view.html":
            # update element table
            
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            # convert POST content into a dictionary
            e_data = urllib.parse.parse_qs( body.decode( 'utf-8' ) )

            message = ""

            if e_data["status"][0] == "add":
                # add element
                try:
                    db['Elements'] = ( int(e_data["number"][0]), 
                                    e_data["symbol"][0],
                                    e_data["name"][0], 
                                    e_data["c1"][0], 
                                    e_data["c2"][0], 
                                    e_data["c3"][0], 
                                    int(e_data["radius"][0]) )
                    message = "table successfully updated"

                    self.send_response( 200 )
                    
                except ValueError:
                    message = "Please enter a number for both '#' and 'Radius'"
                    self.send_response(400)

                except sqlite3.IntegrityError:
                    message = "This element code already exists!"
                    self.send_response(400)

                except KeyError:
                    message = "Please fill in all of the data!"
                    self.send_response(400)
                    
                self.send_header( "Content-type", "text/plain" )
                self.send_header( "Content-length", len(message) )
                self.end_headers()

                self.wfile.write( bytes( message, "utf-8" ) )

                
            elif e_data["status"][0] == "remove":
                # remove element
                db.removeElement( e_data["element_code"][0] )

                message = "table successfully updated"

                self.send_response( 200 )
                self.send_header( "Content-type", "text/plain" )
                self.send_header( "Content-length", len(message) )
                self.end_headers()

                self.wfile.write( bytes( message, "utf-8" ) )
        
        elif self.path == "/sdf_upload.html":
            # handle sdf_upload

            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            # convert POST content into a dictionary
            data = urllib.parse.parse_qs( body.decode( 'utf-8' ) )

            try:
                filename = data["filename"][0].replace( "C:\\fakepath\\", "")

                fp = open( filename )
                db.add_molecule( data["name"][0], fp )

                message = "sdf file uploaded to database"

                self.send_response( 200 )
            
            except sqlite3.IntegrityError:
                message = "This molecule name already exists!"
                self.send_response(400)

            except ValueError:
                message = "This is not a valid sdf file!"
                self.send_response(400)

            except KeyError:
                message = "You are missing some data!"
                self.send_response(400)
                
            self.send_header( "Content-type", "text/plain" )
            self.send_header( "Content-length", len(message) )
            self.end_headers()

            self.wfile.write( bytes( message, "utf-8" ) )

        elif self.path == "/svg_view.html":
            # handle molecule display
            global svg_code
            global molname
            global mol

            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            # convert POST content into a dictionary
            data = urllib.parse.parse_qs( body.decode( 'utf-8' ) )

            try:
                if (data["status"][0] == "view"):
                    molname = data["molname"][0]
                    mol = db.load_mol( molname )

                MolDisplay.radius = db.radius()
                MolDisplay.element_name = db.element_name()
                MolDisplay.header += db.radial_gradients()

                # add any default colours
                MolDisplay.header += db.default_gradients( mol )    

                if (data["status"][0] == "rotate"):
                    x = 0
                    y = 0
                    z = 0

                    if ("x" in data.keys()):
                        x = int(data["x"][0])
                    if "y" in data.keys():
                        y = int(data["y"][0])
                    if "z" in data.keys():
                        z = int(data["z"][0])

                    mx = molecule.mx_wrapper(x, y, z)
                    mol.xform( mx.xform_matrix )

                svg_code = mol.svg()

                message = "svg code received"
                
                self.send_response( 200 )
            
            except ValueError:
                message = "Please enter numbers!"
                self.send_response(400)
                
            self.send_header( "Content-type", "text/plain" )
            self.send_header( "Content-length", len(message) )
            self.end_headers()

            self.wfile.write( bytes ( message, "utf-8" ) )
            
            
        else:
            self.send_response( 404 )
            self.end_headers()
            self.wfile.write( bytes( "404: not found", "utf-8" ) )

httpd = HTTPServer( ( 'localhost', int(sys.argv[1]) ), MyHandler )
httpd.serve_forever()
            