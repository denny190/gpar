#!/usr/bin/python3

import sys
import re

###Passed arguments from bondlength.sh
cwd = os.getcwd()
file_path = sys.argv[1]
file_name = sys.argv[2]

header_line_nums = []
footer_line_nums = []

archive_header = r'1\1'
archive_footer = r'\\@'

###Open the logfile
with open(file_path) as f:
    lines = f.readlines()

###Find number of archive entries and identify lines where headers and footers are located
for line in lines:
    if line.find(archive_header):
        header_line_nums.append(lines.index(line))

    if line.find(archive_footer):
        footer_line_nums.append(lines.index(line))

###If the num
if (len(header_line_nums) != len(footer_line_nums)):
    print(("[ERROR] Number of archiv headers and footers is not equal. Please manually check whether logfile %s is written out correctly!") % (file_path))
    print("[EOF] EXITING.")
    exit(1)

###For each instance of archive entry into the file split each info tab (denomitated by \) into a separate newline
for job in range(len(header_line_nums)):
    whole_archive = lines[archive_header:archive_footer]
    split_archive = whole_archive.split(r'/')
