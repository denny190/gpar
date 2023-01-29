#!/usr/bin/python3
import os
import re
import sys
import linecache
import time

#
start_time = time.time()
print(">> Python Parser Started")
cwd = os.getcwd()

# Initializing all options
opt = False 
freq = False
td = False

scf = False
coords = False
mulliken = False
bonds = False
angles = False
dihedrals = False

# Opening config file
path = cwd + "/tmp/runconfig.cfg.tmp"
config = open(path, 'r')

###

def _splitConfigLine(config_line):
    file_path = (config_line.split(":"))[0]
    line_pointer = (config_line.split(":"))[1]

###
def LoadConfig(configfile):
    
    global opt, freq, td, scf, coords, mulliken, bonds, angles, dihedrals
    
    if "opt=true" in configfile:
        opt = True
    if "freq=true" in configfile:
        freq = True
    if "td=true" in configfile:
        td = True

    if "scf=true" in configfile:
        scf = True 
    if "coords=true" in configfile:
        coords = True
    if "mulliken=true" in configfile:
        mulliken = True
    if "bonds=true" in configfile:
        bonds = True
    if "angles=true" in configfile:
        angles = True
        dihedrals = True


### 
LoadConfig(config)

LoadArchive()

if (coords == True):
    ExtractCoords()

if (bonds == True) or (angles == True) or (dihedrals == True):
    ExtractParams()

if (mulliken == True):
    ExtractMulliken()

if (scf == True):
    ExtractSCF  

assembleOutput()
