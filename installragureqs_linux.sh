#!/bin/bash

#create and activate environment
python3 -m venv venv
source venv/bin/activate

# Install requirements

pip install -r requirements.txt --verbose


#install the browser driver

patchright install chromium
