# !/bin/bash
# Configuration and startup of the IOL for the COCOON Programmable Node (CPN) 
# University of Glasgow, 2025 

# IOL Configuration
IOL_NORTHBOUND_IP='127.0.0.1'
IOL_NORTHBOUND_PORT=5000

# Startup of the IOL 
echo "Starting up the IOL broker"
cd IOL/
./iol_broker.py $IOL_NORTHBOUND_IP $IOL_NORTHBOUND_PORT 

#bash
