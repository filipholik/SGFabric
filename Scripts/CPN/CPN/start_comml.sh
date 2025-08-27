# !/bin/bash
# Configuration and startup of the COMML for the COCOON Programmable Node (CPN) 
# University of Glasgow, 2025 

# COMML Configuration
DPID=1
IOL_IP='127.0.0.1'
IOL_PORT='9000'
INTERFACES_LIST='enp0s3 enp0s8' #Check with ifconfig
SOFTSWITCH=1 #Set to 0 for DPDK 

# Debug 
#echo $DPID
#echo "'$IOL_IP:$IOL_PORT'"

# Startup of the COMML 
if [ $SOFTSWITCH -eq 1 ]; then  
    # Softswitch COMML 
    echo "Starting up the SoftSwitch COMML"
    sudo ./COMML/softswitch/softswitch --dpid=$DPID --controller="'$IOL_IP:$IOL_PORT'" --promiscuous $INTERFACES_LIST

else
    # DPDK COMML 
    echo "Starting up the DPDK COMML"
fi



#bash
