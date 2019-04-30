import os
from rs_startup import rs_startup
import pip
import sys


# Make sure required modules are installed
with open('../../../../../../../../omod/src/main/webapp/requirements.txt') as f:
    for line in f:
        pip.main(['install', '-U', line])

# Inserting image paths and facial features into OpenMRS roles table
npz_file = './rs_feat.npz'
if os.path.isfile(npz_file):
    rs_startup()
    os.remove(npz_file)
