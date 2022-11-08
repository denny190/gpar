import sys
import re

###Passed arguments from bondlength.sh
cwd = os.getcwd()
file_path = sys.argv[1]

###Open the logfile
with open(file_path) as f:
    lines = f.readlines()

###Find number of archive jobs