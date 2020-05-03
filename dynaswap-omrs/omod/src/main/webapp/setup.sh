#!/bin/bash

# get current directory (should be inside dynaswap-omrs/omod/src/main/webapp)
dir=$(pwd)

# install python packages
pip3 install -r requirements.txt

# download and extract face models
cd $dir"/DynaSwapApp/services/"
bash face_models.sh
cd $dir

# insert reference subject features and image paths into databse
cd $dir"/DynaSwapApp/services/data/"
python3 rs_insert.py
cd $dir

# run django server
python3 manage.py runserver 0.0.0.0:8000
