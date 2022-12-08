#!/usr/bin/python3

import os
import re
import sys

runconfig = sys.argv[1]
filtered_paths = sys.argv[2]

def getConfig(configfile):

    options_array = []

    index_cfg_header = 0
    index_cfg_footer = configfile.index("--OPTIONS_END--")

    for line in range(index_cfg_header, index_cfg_footer - 1):
        options_array.append(configfile[line])

###Retrieves options and locations from the config and returns arrays with which the rest of the script works
getConfig()

###Processes retrieved config and discerns what data to retrieve and what data to ignore based on the passed config
###Will probably have to pass a variable that specifies what to extract from each individual file in the following extractParams function
processData()

###Extracting parameters that are specified for each logfile individually - will probably be wrapped in a for cycle later on
extractParams()

###Assembles the collected data in a user-readable csv output.
assembleOutput()