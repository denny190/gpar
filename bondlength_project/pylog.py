#!/usr/bin/python3
import os
import re
import sys

###Initializing all options and setting them false
opt=False
freq=False
td=False

scf=False
coords=False
mulliken=False
bonds=False
angles=False

###Defining job identification strings
optString = "FOpt"
tdString = "TD-DFT" ##Not sure about this
freqString = "Freq"

###Defining archive indices arrays
archive_headers_array = []
archive_footers_array = []

###Opening file paths that are passed as arguments
runconfig = open(sys.argv[1], "w")

with open(sys.argv[2]) as f:
        paths = f

###Getting options for current run
def getConfig(configfile):

    ###Setting option variables as globals so they can be accessed and changed within this function
    global opt
    global freq
    global td
    global scf
    global coords
    global mulliken
    global bonds
    global angles

    options_array = []

    ###Saves passed options in an array
    index_cfg_header = 0
    index_cfg_footer = configfile.index("--OPTIONS_END--")

    for line in range(index_cfg_header, index_cfg_footer - 1):
        options_array.append(configfile[line])
    
    ###Checks the state of each option (depending on its presence in options array) and changes its global value if its in the configfile
    if "opt" in options_array:
        opt = True
    if "freq" in options_array:
        freq = True
    if "td" in options_array:
        td = True

    if "scf" in options_array:
        scf = True
    if "coords" in options_array:
        coords = True
    if "mulliken" in options_array:
        mulliken = True
    if "bonds" in options_array:
        bonds = True
    if "angles" in options_array:
        angles = True

    return options_array

###Filtering archives by job type
def filterLogs(configfile):

    selected_jobs = []
    global archive_headers_array
    global archive_footers_array
    
    ###Loads the part of the config file that contains archive header and footer indices and filepaths
    archive_head_begin = configfile.index("ARCHIVE_HEADERS_START:")
    archive_head_end = configfile.index("ARCHIVE_HEADERS_END:") 
    archive_headers_array = configfile[archive_head_begin:archive_head_end]

    archive_foot_begin = configfile.index("ARCHIVE_FOOTERS_START:") 
    archive_foot_end = configfile.index("ARCHIVE_FOOTERS_END:")
    archive_footers_array = configfile[archive_foot_begin:archive_foot_end]

    ###Checks presence of requested job in archive for each line in config header array
    for line in archive_headers_array:
        
        ###Boolean that allows to pop filepath from config if it stays false
        found_match = False

        configline = line.split(":")
        file_path = configline[0]
        archive_head_index = configline[1]

        with open(file_path) as f:
            examined_file = f

        if (opt == True):
            if optString in examined_file[archive_head_index]:
                selected_jobs.append(file_path)
                found_match = True

        elif (freq == True):
            if freqString in examined_file[archive_head_index]:
                selected_jobs.append(file_path)
                found_match = True

        elif (td == True):
            if tdString in examined_file[archive_head_index]:
                selected_jobs.append(file_path)
                found_match = True
        
        ###Removes the archive entry from header array and corresponding index in footer array if no match found
        if (found_match == False):
            archive_headers_array.pop(line.index())
            archive_footers_array.pop(line.index())



###Retrieves options and locations from the config and returns arrays with which the rest of the script works
config_array = getConfig(runconfig)

###Filters logfiles by desired job types
filterLogs(runconfig)

###Processes retrieved config and discerns what data to retrieve and what data to ignore based on the passed config
###Will probably have to pass a variable that specifies what to extract from each individual file in the following extractParams function
processData()

###Extracting parameters that are specified for each logfile individually - will probably be wrapped in a for cycle later on
extractParams()

###Assembles the collected data in a user-readable csv output.
assembleOutput()                                