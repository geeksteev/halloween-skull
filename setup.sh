#!/bin/bash

python3 -m venv venv
source venv/bin/activate
sudo apt install -y git python3-pip python3-opencv libcamera-dev
pip3 install -r requirements.txt