#!/usr/bin/env bash

sudo apt-get update
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.9 -y
sudo apt-get install git-all -y
sudo apt install python3-pip -y
sudo apt-get install python3-distutils -y
sudo apt-get install python3-apt -y
sudo apt-get install build-essential -y
sudo apt install python-is-python3 -y

make install
python3.9 -m pip install -r requirements.txt