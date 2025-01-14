#! /usr/bin/sh 
# Example file of recommended topology startup process 
cd topologies
sudo killall softswitch
sudo mn --clean
sudo python3 ./SGFabric.py
#cd ../GUI
#./initDatabase.sh
#bash

