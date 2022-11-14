#!/usr/bin/python3

import os
import re
import sys

###Passed arguments from bondlength.sh
cwd = os.getcwd()
file_path = sys.argv[1]
file_name = sys.argv[2]

archive_header_lines = []
archive_footer_lines = []

bond_list = []

archive_header = r"1\1"
archive_footer = "\\@"
job_type = "FOpt"
btable_string ="!   Optimized Parameters   !"

###Open the logfile
with open(file_path) as f:
    lines = f.readlines()

###Find number of archive entries and identify lines where headers and footers are located
for line in lines:
    if archive_header in line:
        archive_header_lines.append(lines.index(line))

    if archive_footer in line:
        archive_footer_lines.append(lines.index(line))

    ###Finds and reads the table containing connectivity parameters
    if btable_string in line:
        counter = 5

        while "R(" in lines[lines.index(line) + counter]:
            comma_index = lines[lines.index(line) + counter].index(",")
            bond_list.append([lines[lines.index(line) + counter][comma_index - 1],lines[lines.index(line) + counter][comma_index + 1]])
            counter += 1

print(bond_list)

#
if (len(archive_header_lines) != len(archive_footer_lines)):
    print(("[ERROR] Number of archive headers and footers is not equal. Please manually check whether logfile %s is written out correctly!") % (file_path))
    print("[EOF] EXITING.")
    exit(1)

###For each instance of archive entry into the file split each info tab (denomitated by \) into a separate newline
for job in range(len(archive_header_lines)):
    whole_archive = lines[archive_header_lines[job]:archive_footer_lines[job]]

    #If first line of archive contains the desired job tag
    if job_type in whole_archive[0]:
        ###Strip newline characters from end of each line
        whole_archive = [item.strip() for item in whole_archive]
        #Join all elems in whole_archive to allow splitting via \ as denominator (havent figured out a better way to do this)
        string_archive = ''.join(whole_archive)

        split_archive = string_archive.split("\\")
        
        split_archive = split_archive[2:]
        for x in split_archive:
            print(x)
        print(bond_list)

        job_type = split_archive[1]
        functional = split_archive[2]
        basis_set = split_archive[3]
        

        ###BOND LENGTH CALC: In cartesian space bond length between A and B is defined as r = sqrt{ [x(B) - x(A)]^2 + [y(B) - y(A)]^2 + [z(B) - z(A)]^2 }

    else:
        continue