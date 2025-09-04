# !/bin/bash
# Configuration and startup of the COMML for the COCOON Programmable Node (CPN) 
# University of Glasgow, 2025 

# COMML Configuration
DPID=1
IOL_SOUTHBOUND_IP='127.0.0.1'
IOL_SOUTHBOUND_PORT='9000'
INTERFACES_LIST='enp1s0 enp2s0 enp3s0 enp4s0' # Check with ifconfig
#INTERFACES_LIST='enp0s3 enp0s8' # VM testing version
SOFTSWITCH=1 #Set to 0 for DPDK 

# Debug 
#echo $DPID
#echo "$IOL_SOUTHBOUND_IP:$IOL_SOUTHBOUND_PORT"

# Startup of the COMML 
if [ $SOFTSWITCH -eq 1 ]; then  
    # Softswitch COMML 
    echo "Starting up the softswitch COMML"
    sudo ./COMML/softswitch/softswitch --dpid=$DPID --controller="$IOL_SOUTHBOUND_IP:$IOL_SOUTHBOUND_PORT" --promiscuous $INTERFACES_LIST

else
    # DPDK COMML 
    echo "Starting up the DPDK COMML"
    sudo -i
    echo 1024 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
    cat /proc/meminfo
    modprobe vfio-pci
    dpdk-devbind.py --bind=vfio-pci 0000:01:00.0 # Adjust according to the previous output
    dpdk-devbind.py --bind=vfio-pci 0000:02:00.0 # Adjust according to the previous output

    cd COMML/dpdkswitch/build/
    sudo ./bpfabric -l 0-1 -n 4 -- -q 1 -p 3 -d 1 -c '$IOL_SOUTHBOUND_IP:$IOL_SOUTHBOUND_PORT' # Adjust accordingly
fi


#bash
