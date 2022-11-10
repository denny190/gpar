#!/usr/bin/python3

import sys
import os
import re

###Passed arguments from bondlength.sh
cwd = os.getcwd()
file_path = sys.argv[1]
file_name = sys.argv[2]

header_line_nums = []
footer_line_nums = []

archive_header = r"1\1"
archive_footer = "\\@"
job_type = "FOpt"

###Open the logfile
with open(file_path) as f:
    lines = f.readlines()

###Find number of archive entries and identify lines where headers and footers are located
for line in lines:
    if archive_header in line:
        header_line_nums.append(lines.index(line))

    if archive_footer in line:
        footer_line_nums.append(lines.index(line))

#
if (len(header_line_nums) != len(footer_line_nums)):
    print(("[ERROR] Number of archive headers and footers is not equal. Please manually check whether logfile %s is written out correctly!") % (file_path))
    print("[EOF] EXITING.")
    exit(1)

###For each instance of archive entry into the file split each info tab (denomitated by \) into a separate newline
for job in range(len(header_line_nums)):
    whole_archive = lines[header_line_nums[job]:footer_line_nums[job]]

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

        job_type = split_archive[1]
        functional = split_archive[2]
        basis_set = split_archive[3]
        

    else:
        continue