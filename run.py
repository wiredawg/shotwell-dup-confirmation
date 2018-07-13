#!/usr/bin/env python3
"""
Processes a Shotwell import report's duplicates section and produces an HTML table
with two columns showing the duplicate images side-by-side for easy visual confirmation.
...Just to help me gain confidence in Shotwell's results.
"""

import sys, os, re
from glob import glob
from math import ceil
import json

# ----------------------------------------------------------------------------

SCRIPTNAME = os.path.basename( sys.argv[0] )
ERROR = "%s: -ERROR- "   % SCRIPTNAME
WARN  = "%s: -Warning- " % SCRIPTNAME
INFO  = "%s: -Info- "    % SCRIPTNAME

def Say( lvl, msg ):
    print( "%s %s" % (lvl, msg) )

# ----------------------------------------------------------------------------

class Report( object ):
    def __init__( self ):
        self.attempt = 0
        self.actual  = 0
        self.duplicates = []
        self.path_map = {}

    def path_adjust( self, p ):
        for x,y in self.path_map.items():
            if p.startswith(x):
                return p.replace(x, y)
        return p
    
    def toHTML( self, filename=None, dups_per_page=50 ):
        num_dups = len( self.duplicates )
        page_cnt = ceil( num_dups / dups_per_page )
        Say( INFO, "# of pages: %d" % page_cnt )
        pages = {}
        for p_cntr in range( page_cnt ):
            this_filename = filename
            html = """\
            <html>
                <head></head>
            <body>
                <H1>Shotwell Report</H1>
                <P>%ATTEMPT%/%ACTUAL% files imported</P>
                <H2>Duplication Table</H2>
                <table>
                    %TABLE_ROWS%
                </table>
            </body>
            </html>
            """

            table_rows = []
            dup_ptr_start = p_cntr * dups_per_page
            dup_ptr_end   = ( (1 + p_cntr) * dups_per_page) - 1
            for i in range( dup_ptr_start, dup_ptr_end+1 ):
                try:
                    dup = self.duplicates[i]
                except IndexError:
                    # Reached the end of the line
                    break
                p0 = self.path_adjust( dup[0] )
                p1 = self.path_adjust( dup[1] )
                table_rows.append( '<TR><TD><P>%s</P></TD><TD><P>%s</P></TD></TR>' % (p0, p1) )
                table_rows.append( '<TR><TD><IMG SRC="%s" HEIGHT=200 WIDTH=200></TD><TD><IMG SRC="%s" HEIGHT=200 WIDTH=200></TD></TR>' % (p0, p1) )
                table_rows.append( '<TR><TD><P></P></TD><TD><P></P></TD></TR>' )
            
            html = html.replace( "%ATTEMPT%", str(self.attempt) )
            html = html.replace( "%ACTUAL%", str(self.actual) )
            html = html.replace( "%TABLE_ROWS%", str.join("\n", table_rows) )
            html = re.sub( r'^'+r' '*8, '', html, flags=re.M )

            if this_filename:
                if page_cnt > 1:
                    fname,ext = os.path.splitext( this_filename )
                    this_filename = "%s-%d%s" % ( fname, p_cntr, ext )
                Say( INFO, "Writing HTML file: %s" % this_filename )
                fp = open( this_filename, 'w' )
                fp.write( html )
                fp.close()
            else:
                filename = p_cntr

            pages[this_filename] = html

        return pages

# ----------------------------------------------------------------------------

def gen_html_from_log( log, path_map_file=None ):
    fp = open( log, 'r' )
    lines = fp.readlines()
    fp.close()

    rpt = Report()

    if path_map_file:
        path_map = json.load(open(path_map_file))
        rpt.path_map = path_map
    
    first_dup = ""
    for i,line in enumerate(lines):
        if line.find("Attempted to import") >= 0:
            m = re.match( r'^Attempted to import (\d+) files. Of these, (\d+) files.*$', line )
            if m:
                rpt.attempt = m.group(1)
                rpt.actual  = m.group(2)
        elif line.find("duplicates existing media item") >= 0:
            m = re.match( r'^(.*?) duplicates existing media item', line )
            if m:
                first_dup = m.group(1)
        elif first_dup != "":
            rpt.duplicates.append( [ first_dup, line.lstrip().rstrip() ] )
            first_dup = ""
        else: 
            continue

    Say( INFO, "# of duplicates: %d" % len( rpt.duplicates  ) )
    html_file = "server_root/%s.html" % os.path.basename(log)
    rpt.toHTML(html_file)

    return 0


# ----------------------------------------------------------------------------

def script_entry( args ):
    Say( INFO, "Starting..." )

    if len( args ) < 1:
        print( "usage: %s <directory with logfiles> [path_map_file]" % SCRIPTNAME )
        return 1

    logdir = args[0]
    try:
        path_map_file = args[1]
    except IndexError:
        path_map_file = None

    logs = glob( "%s/*.txt" % logdir )
    Say( INFO, "Number of log files: %s" % len(logs) )

    log_status = {}
    for log in sorted(logs):
        Say( INFO, "Running: %s" % log )
        log_status[log] = "running"
        rc = gen_html_from_log( log, path_map_file )
        if rc:
            log_status[log] = "failed"
            Say( INFO, "Failure..." )
        else: 
            log_status[log] = "completed"
            Say( INFO, "Success..." )

    return 0

# ----------------------------------------------------------------------------
if __name__ == "__main__" : sys.exit( script_entry( sys.argv[1:] ) )
